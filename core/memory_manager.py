# core/memory_manager.py
"""
Memory Manager for Othello.

Provides a structured interface around DB memory_entries for storing and retrieving
reflections, goal updates, and other memory entries.

Migrated from file-based agentic_memory.json to Postgres (Phase 2).

Usage:
    from core.memory_manager import MemoryManager
    
    memory = MemoryManager()
    
    # Add a memory entry
    memory.append_memory({
        "type": "goal_update",
        "goal_id": 5,
        "content": "Created a 3-step plan to learn Python"
    })
    
    # Get recent memories
    recent = memory.get_recent_memories(limit=10)
    
    # Get goal-specific memories
    goal_memories = memory.get_relevant_memories(goal_id=5, limit=5)
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from db.memory_entries_repository import append_memory_entry, list_memory_entries, list_memories_by_goal


class MemoryManager:
    """
    DB-backed memory manager for Othello.
    
    Stores memory entries in Postgres 'memory_entries' table.
    """
    
    def __init__(self, memory_file: Optional[Path] = None, user_id: str = "1") -> None:
        """
        Initialize the MemoryManager.
        
        Args:
            memory_file: Deprecated (ignored). Kept for backward compatibility.
            user_id: The user ID to scope memories to. Defaults to "1".
        """
        self.logger = logging.getLogger("MemoryManager")
        self.user_id = user_id
        self.logger.info(f"MemoryManager: Initialized (DB-backed) for user_id={self.user_id}")
    
    def _map_db_entry(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map DB row to legacy memory entry format."""
        meta = row.get("metadata") or {}
        return {
            "type": row.get("kind", "general"),
            "content": row.get("content", ""),
            "timestamp": row.get("created_at").isoformat() if row.get("created_at") else None,
            **meta
        }

    def append_memory(self, entry: Dict[str, Any]) -> bool:
        """
        Append a new memory entry to DB.
        
        The entry should include:
        - type: str (e.g., "reflection", "goal_update", "insight")
        - content: str (the actual memory text)
        - goal_id: int (optional, if memory is goal-specific)
        
        Args:
            entry: Memory entry dictionary
        
        Returns:
            True if successful, False otherwise
        """
        # Validate required fields
        if "content" not in entry:
            self.logger.error("MemoryManager: Cannot append memory without 'content' field")
            return False
        
        kind = entry.get("type", "general")
        content = entry["content"]
        
        # Metadata includes everything else
        metadata = {k: v for k, v in entry.items() if k not in ("type", "content")}
        
        try:
            res = append_memory_entry(self.user_id, kind, content, metadata)
            if res:
                self.logger.info(f"MemoryManager: Added memory entry to DB (id={res.get('id')}, type={kind})")
                return True
            return False
        except Exception as e:
            self.logger.error(f"MemoryManager: Failed to append memory to DB: {e}")
            return False
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent memory entries from DB.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of memory entries in reverse chronological order (newest first)
        """
        try:
            rows = list_memory_entries(self.user_id, limit=limit)
            self.logger.info(f"MemoryManager: Read {len(rows)} recent memories from DB")
            return [self._map_db_entry(row) for row in rows]
        except Exception as e:
            self.logger.error(f"MemoryManager: Failed to get recent memories from DB: {e}")
            return []
    
    def get_relevant_memories(self, goal_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant memories, optionally filtered by goal_id.
        
        Args:
            goal_id: Optional goal ID to filter by
            limit: Maximum number of entries to return
        
        Returns:
            List of relevant memory entries in reverse chronological order
        """
        try:
            if goal_id is not None:
                rows = list_memories_by_goal(self.user_id, goal_id, limit=limit)
            else:
                rows = list_memory_entries(self.user_id, limit=limit)
            
            return [self._map_db_entry(row) for row in rows]
        except Exception as e:
            self.logger.error(f"MemoryManager: Failed to get relevant memories from DB: {e}")
            return []
    
    def clear_all_memories(self) -> bool:
        """
        Clear all memories.
        
        Note: In DB mode, this is dangerous/not implemented for safety.
        Returns False to indicate no-op.
        """
        self.logger.warning("MemoryManager: clear_all_memories is not supported in DB mode (safety)")
        return False
    
    def get_memory_count(self) -> int:
        """
        Get the total number of memories stored.
        
        Returns:
            Number of memory entries (approximate/limited)
        """
        try:
            rows = list_memory_entries(self.user_id, limit=1000)
            return len(rows)
        except:
            return 0
