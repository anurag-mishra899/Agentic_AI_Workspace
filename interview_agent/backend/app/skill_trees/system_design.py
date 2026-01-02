SYSTEM_DESIGN_SKILL_TREE = {
    "scaling": {
        "name": "Scaling Concepts",
        "topics": {
            "horizontal_vertical": {
                "name": "Horizontal vs Vertical Scaling",
                "skills": [
                    "scaling_tradeoffs",
                    "stateless_design",
                    "session_management"
                ]
            },
            "load_balancing": {
                "name": "Load Balancing",
                "skills": [
                    "load_balancer_types",
                    "lb_algorithms",
                    "health_checks"
                ]
            },
            "caching": {
                "name": "Caching Strategies",
                "skills": [
                    "cache_patterns",
                    "cache_invalidation",
                    "distributed_caching",
                    "cdn_usage"
                ]
            }
        }
    },
    "data_storage": {
        "name": "Data Storage",
        "topics": {
            "sql_nosql": {
                "name": "SQL vs NoSQL",
                "skills": [
                    "database_selection",
                    "acid_properties",
                    "nosql_types"
                ]
            },
            "sharding": {
                "name": "Sharding",
                "skills": [
                    "sharding_strategies",
                    "shard_key_selection",
                    "cross_shard_queries"
                ]
            },
            "replication": {
                "name": "Replication",
                "skills": [
                    "master_slave_replication",
                    "multi_master_replication",
                    "replication_lag"
                ]
            },
            "indexing": {
                "name": "Indexing",
                "skills": [
                    "index_types",
                    "index_selection",
                    "query_optimization"
                ]
            }
        }
    },
    "consistency_availability": {
        "name": "Consistency & Availability",
        "topics": {
            "cap_theorem": {
                "name": "CAP Theorem",
                "skills": [
                    "cap_tradeoffs",
                    "partition_tolerance",
                    "consistency_models"
                ]
            },
            "eventual_consistency": {
                "name": "Eventual Consistency",
                "skills": [
                    "eventual_consistency_patterns",
                    "conflict_resolution",
                    "vector_clocks"
                ]
            },
            "consensus": {
                "name": "Consensus Protocols",
                "skills": [
                    "paxos_basics",
                    "raft_protocol",
                    "leader_election"
                ]
            }
        }
    },
    "reliability": {
        "name": "Reliability",
        "topics": {
            "fault_tolerance": {
                "name": "Fault Tolerance",
                "skills": [
                    "redundancy",
                    "failover_strategies",
                    "graceful_degradation"
                ]
            },
            "circuit_breakers": {
                "name": "Circuit Breakers",
                "skills": [
                    "circuit_breaker_pattern",
                    "retry_strategies",
                    "bulkhead_pattern"
                ]
            },
            "monitoring": {
                "name": "Monitoring & Alerting",
                "skills": [
                    "metrics_collection",
                    "logging_strategies",
                    "alerting_best_practices"
                ]
            }
        }
    },
    "communication": {
        "name": "System Communication",
        "topics": {
            "api_design": {
                "name": "API Design",
                "skills": [
                    "rest_design",
                    "graphql_design",
                    "grpc_design"
                ]
            },
            "messaging": {
                "name": "Messaging Systems",
                "skills": [
                    "message_queues",
                    "pub_sub_systems",
                    "event_driven_architecture"
                ]
            },
            "protocols": {
                "name": "Protocols",
                "skills": [
                    "http_https",
                    "websockets",
                    "long_polling"
                ]
            }
        }
    },
    "security": {
        "name": "Security",
        "topics": {
            "authentication": {
                "name": "Authentication",
                "skills": [
                    "auth_mechanisms",
                    "oauth_openid",
                    "jwt_tokens"
                ]
            },
            "authorization": {
                "name": "Authorization",
                "skills": [
                    "rbac",
                    "abac",
                    "permission_models"
                ]
            },
            "data_security": {
                "name": "Data Security",
                "skills": [
                    "encryption_at_rest",
                    "encryption_in_transit",
                    "key_management"
                ]
            }
        }
    }
}
