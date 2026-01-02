from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import asyncio
import json
import base64

from app.database import get_db_context
from app.services.auth import decode_token, get_user_by_id
from app.services.session_manager import session_manager
from app.services.azure_realtime import AzureRealtimeClient
from app.models.session import InterviewSession

router = APIRouter(tags=["websocket"])


async def authenticate_websocket(token: str) -> int:
    """Authenticate WebSocket connection and return user_id."""
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return int(user_id)


@router.websocket("/v1/ws/session/{session_id}")
async def websocket_session(
    websocket: WebSocket,
    session_id: int,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time voice interview session.

    Protocol:
    - Client sends: {"type": "audio", "data": "<base64 audio>"} for audio chunks
    - Client sends: {"type": "control", "action": "mute|unmute|end"}
    - Server sends: {"type": "audio", "data": "<base64 audio>"} for AI audio
    - Server sends: {"type": "transcript", "role": "user|assistant", "text": "..."}
    - Server sends: {"type": "status", "status": "connected|speaking|processing|error"}
    """
    # Authenticate
    try:
        user_id = await authenticate_websocket(token)
    except HTTPException:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # Verify session ownership and status
    with get_db_context() as db:
        session = db.query(InterviewSession).filter(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
            InterviewSession.status == "active"
        ).first()

        if not session:
            await websocket.close(code=4004, reason="Session not found or not active")
            return

        persona = session.persona
        depth_mode = session.depth_mode
        domains = session.domains
        declared_weak_areas = session.declared_weak_areas
        resume_text = session.resume_text

    # Accept WebSocket connection
    await websocket.accept()

    # Update session state
    session_manager.set_connection_state(session_id, True)

    # Send initial status
    await websocket.send_json({
        "type": "status",
        "status": "connected",
        "session_id": session_id
    })

    # Create Azure Realtime client
    azure_client = AzureRealtimeClient(
        session_id=session_id,
        persona=persona,
        depth_mode=depth_mode,
        domains=domains,
        declared_weak_areas=declared_weak_areas or [],
        resume_text=resume_text
    )

    try:
        # Connect to Azure Realtime
        await azure_client.connect()

        # Create tasks for bidirectional communication
        receive_task = asyncio.create_task(
            handle_client_messages(websocket, azure_client, session_id)
        )
        send_task = asyncio.create_task(
            handle_azure_messages(websocket, azure_client, session_id)
        )

        # Wait for either task to complete (client disconnect or error)
        done, pending = await asyncio.wait(
            [receive_task, send_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        # Cleanup
        session_manager.set_connection_state(session_id, False)
        await azure_client.disconnect()


async def handle_client_messages(
    websocket: WebSocket,
    azure_client: AzureRealtimeClient,
    session_id: int
):
    """Handle incoming messages from the client."""
    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "audio":
                # Forward audio to Azure
                audio_data = base64.b64decode(data.get("data", ""))
                await azure_client.send_audio(audio_data)

            elif msg_type == "control":
                action = data.get("action")
                if action == "end":
                    break
                elif action == "mute":
                    session_manager.update_speaking_state(session_id, False)
                elif action == "unmute":
                    session_manager.update_speaking_state(session_id, True)

    except WebSocketDisconnect:
        raise


async def handle_azure_messages(
    websocket: WebSocket,
    azure_client: AzureRealtimeClient,
    session_id: int
):
    """Handle incoming messages from Azure Realtime."""
    try:
        async for event in azure_client.receive_events():
            event_type = event.get("type")

            if event_type == "audio":
                # Forward audio to client
                await websocket.send_json({
                    "type": "audio",
                    "data": event.get("data")
                })

            elif event_type == "transcript":
                # Forward transcript and store it
                role = event.get("role")
                text = event.get("text")

                session_manager.add_transcript_entry(session_id, role, text)

                await websocket.send_json({
                    "type": "transcript",
                    "role": role,
                    "text": text
                })

            elif event_type == "turn_detection":
                # User speech state changed
                is_speaking = event.get("is_speaking", False)
                session_manager.update_speaking_state(session_id, is_speaking)

                await websocket.send_json({
                    "type": "status",
                    "status": "speaking" if is_speaking else "listening"
                })

            elif event_type == "error":
                await websocket.send_json({
                    "type": "error",
                    "message": event.get("message", "Unknown error")
                })

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
        raise
