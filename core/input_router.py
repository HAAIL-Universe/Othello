from modules.impatience_detector import ImpatienceDetector
from core.logger import FelloLogger
from core.memory_manager import MemoryManager

class InputRouter:
    """
    Routes incoming user input through FELLO’s processing pipeline.
    Detects impatience, mood, and routes to appropriate engine/module.
    Fully modular for future detectors and hooks.
    """
    
    def __init__(self, enable_impatience=True):
        """
        Initializes the InputRouter.
        :param enable_impatience: Bool flag to enable/disable impatience detection.
        """
        self.enable_impatience = enable_impatience
        self.impatience_detector = ImpatienceDetector() if enable_impatience else None
        self.logger = FelloLogger()
        self.memory_mgr = MemoryManager()
    
    def route_input(self, input_text, context=None):
        """
        Main entry point. Routes input through detection pipeline and returns tags + clean input.
        :param input_text: The raw user input string.
        :param context: Optional dict with additional routing context.
        :return: dict with processed input, tags, and routing target.
        """
        tags = {}
        memories = []
        
        # Impatience detection
        if self.enable_impatience and self.impatience_detector:
            impatience_level = self.impatience_detector.analyze(input_text)
            tags['impatience_level'] = impatience_level
        
        # Fetch relevant memories for goal-related inputs
        if context and 'goal_id' in context:
            goal_id = context['goal_id']
            try:
                # Get recent memories related to this goal
                memories = self.memory_mgr.get_relevant_memories(goal_id=goal_id, limit=3)
                tags['has_goal_memories'] = len(memories) > 0
                tags['memory_count'] = len(memories)
            except Exception as e:
                self.logger.log_event('memory_fetch_error', {
                    'goal_id': goal_id,
                    'error': str(e)
                })
        
        # Future: mood detection, energy tagging, etc.
        # tags['mood'] = self.detect_mood(input_text)
        
        self.log_input(input_text, tags)
        
        # Determine routing target (stubbed for now)
        routing_target = 'default_engine'
        
        return {
            'input': input_text,
            'tags': tags,
            'routing_target': routing_target,
            'memories': memories
        }
    
    def log_input(self, input_text, tags):
        """
        Logs the input and tags for traceability.
        :param input_text: The raw input.
        :param tags: Dict of tags applied during processing.
        """
        self.logger.log_event('input_received', {
            'input': input_text,
            'tags': tags
        })

    def get_memory_context_string(self, memories):
        """
        Convert memory entries into a formatted context string for LLM prompts.
        
        :param memories: List of memory entry dicts
        :return: Formatted string summarizing the memories
        """
        if not memories:
            return ""
        
        lines = ["Recent relevant memories:"]
        for mem in memories:
            timestamp = mem.get('timestamp', 'unknown time')
            content = mem.get('content', '')
            mem_type = mem.get('type', 'general')
            lines.append(f"- [{mem_type} @ {timestamp}]: {content}")
        
        return "\n".join(lines)

    def is_plan_request(self, message: str) -> bool:
        """
        Detect if the user is explicitly asking to create or update a structured plan.
        
        This classifier identifies plan generation keywords and phrases that should
        trigger the dedicated XML-only planning pipeline instead of conversational mode.
        
        :param message: The user's input message
        :return: True if this appears to be a plan generation request
        """
        text = message.lower()
        
        # Keywords and phrases that indicate plan generation intent
        triggers = [
            "generate a full plan",
            "generate a plan",
            "create a full plan",
            "create a plan",
            "make a full plan",
            "make a plan",
            "plan this goal",
            "plan for this goal",
            "break this goal into steps",
            "break this into steps",
            "break down this goal",
            "turn this into a plan",
            "make a plan for this",
            "can you plan this",
            "help me plan this",
            "build a plan",
            "using your canonical",  # catches "using your canonical <goal_update> schema"
            "<goal_update> schema",
            "xml schema",
        ]
        
        # Check if any trigger phrase appears in the message
        matched = any(trigger in text for trigger in triggers)
        
        if matched:
            self.logger.log_event('plan_request_detected', {
                'message_preview': message[:100]
            })
        
        return matched

    # TODO: Add detect_mood(), pre_processors() as needed for future expansion.
