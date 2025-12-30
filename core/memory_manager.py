# core/memory_manager.py
"""
Memory Manager for Othello.

Provides a structured interface around agentic_memory.json for storing and retrieving
reflections, goal updates, and other memory entries.

This is a simple file-based approach that can later be upgraded to use embeddings
or semantic search for more advanced retrieval.

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

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class MemoryManager:
    """
    Simple JSON-based memory manager for Othello.
    
    Stores memory entries in agentic_memory.json with the following structure:
    [
        {
            "timestamp": "2025-12-08T10:30:00Z",
            "type": "reflection" | "goal_update" | "insight" | ...,
            "goal_id": 5 (optional),
            "content": "The actual memory text"
        },
        ...
    ]
    """
    
    def __init__(self, memory_file: Optional[Path] = None) -> None:
        """
        Initialize the MemoryManager.
        
        Args:
            memory_file: Path to the memory JSON file. If None, uses agentic_memory.json
                        in the project root.
        """
        self.logger = logging.getLogger("MemoryManager")
        
        if memory_file is None:
            # Default to agentic_memory.json in project root
            root = Path(__file__).resolve().parent.parent
            memory_file = root / "agentic_memory.json"
        
        self.memory_file = memory_file
        self.logger.info(f"MemoryManager: Using memory file: {self.memory_file}")
    
    def _load_memories(self) -> List[Dict[str, Any]]:
        """
        Load all memories from the JSON file.
        
        Returns:
            List of memory entries. Returns empty list if file doesn't exist or is invalid.
        """
        global _MEMORY_DB_ONLY_WARNED
        if _PHASE1_DB_ONLY:
            if not _MEMORY_DB_ONLY_WARNED:
                self.logger.warning("MemoryManager: JSON memory disabled in Phase-1 DB-only mode")
                _MEMORY_DB_ONLY_WARNED = True
            return []
        if not self.memory_file.exists():
            self.logger.debug("MemoryManager: Memory file does not exist yet, starting fresh")
            return []
        
        try:
            with self.memory_file.open("r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                memories = json.loads(content)
                
                if not isinstance(memories, list):
                    self.logger.error(f"MemoryManager: Memory file contains non-list data, resetting")
                    return []
                
                return memories
        except json.JSONDecodeError as e:
            self.logger.error(f"MemoryManager: Failed to parse memory file: {e}")
            return []
        except Exception as e:
            self.logger.error(f"MemoryManager: Error reading memory file: {e}")
            return []
    
    def _save_memories(self, memories: List[Dict[str, Any]]) -> bool:
        """
        Save all memories to the JSON file.
        
        Args:
            memories: List of memory entries
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure parent directory exists
            self.memory_file.parent.mkdir(parents=True, exist_ok=True)
            
            with self.memory_file.open("w", encoding="utf-8") as f:
                json.dump(memories, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            self.logger.error(f"MemoryManager: Failed to save memory file: {e}")
            return False
    
    def append_memory(self, entry: Dict[str, Any]) -> bool:
        """
        Append a new memory entry.
        
        The entry should include:
        - type: str (e.g., "reflection", "goal_update", "insight")
        - content: str (the actual memory text)
        - goal_id: int (optional, if memory is goal-specific)
        
        Timestamp will be added automatically if not present.
        
        Args:
            entry: Memory entry dictionary
        
        Returns:
            True if successful, False otherwise
        """
        # Validate required fields
        if "content" not in entry:
            self.logger.error("MemoryManager: Cannot append memory without 'content' field")
            return False
        
        if "type" not in entry:
            self.logger.warning("MemoryManager: Memory entry missing 'type', defaulting to 'general'")
            entry["type"] = "general"
        
        # Add timestamp if not present
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        # Load existing memories
        memories = self._load_memories()
        
        # Append new entry
        memories.append(entry)
        
        # Save back to file
        success = self._save_memories(memories)
        
        if success:
            self.logger.info(f"MemoryManager: Added memory entry (type={entry['type']}, goal_id={entry.get('goal_id', 'N/A')})")
        
        return success
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent memory entries.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of memory entries in reverse chronological order (newest first)
        """
        memories = self._load_memories()
        
        # Sort by timestamp (newest first)
        try:
            sorted_memories = sorted(
                memories,
                key=lambda m: m.get("timestamp", ""),
                reverse=True
            )
        except Exception as e:
            self.logger.error(f"MemoryManager: Failed to sort memories: {e}")
            sorted_memories = memories
        
        return sorted_memories[:limit]
    
    def get_relevant_memories(self, goal_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get relevant memories, optionally filtered by goal_id.
        
        This is a simple heuristic implementation. Future versions can use
        semantic search or embeddings for better relevance matching.
        
        Args:
            goal_id: Optional goal ID to filter by
            limit: Maximum number of entries to return
        
        Returns:
            List of relevant memory entries in reverse chronological order
        """
        memories = self._load_memories()
        
        # Filter by goal_id if provided
        if goal_id is not None:
            filtered = [m for m in memories if m.get("goal_id") == goal_id]
        else:
            filtered = memories
        
        # Sort by timestamp (newest first)
        try:
            sorted_memories = sorted(
                filtered,
                key=lambda m: m.get("timestamp", ""),
                reverse=True
            )
        except Exception as e:
            self.logger.error(f"MemoryManager: Failed to sort memories: {e}")
            sorted_memories = filtered
        
        return sorted_memories[:limit]
    
    def clear_all_memories(self) -> bool:
        """
        Clear all memories (useful for testing or reset).
        
        Returns:
            True if successful, False otherwise
        """
        success = self._save_memories([])
        if success:
            self.logger.info("MemoryManager: Cleared all memories")
        return success
    
    def get_memory_count(self) -> int:
        """
        Get the total number of memories stored.
        
        Returns:
            Number of memory entries
        """
        return len(self._load_memories())


_PHASE1_DB_ONLY = (os.getenv("OTHELLO_PHASE1_DB_ONLY") or "").strip().lower() in ("1", "true", "yes")
_MEMORY_DB_ONLY_WARNED = False
