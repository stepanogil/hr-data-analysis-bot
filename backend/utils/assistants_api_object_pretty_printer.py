import json
import ast
import io
import sys

# Pretty print objects from the OpenAI Assistants API


def complex_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, '__dict__'):
        obj_dict = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, str):
                try:
                    # Attempt to parse a string that looks like a dictionary
                    if value.strip().startswith("{"):
                        value = ast.literal_eval(value)
                    obj_dict[key] = complex_handler(value)
                except (ValueError, SyntaxError):
                    # If it's not a dictionary string, handle normally
                    obj_dict[key] = value
            else:
                obj_dict[key] = complex_handler(value)
        return obj_dict
    elif isinstance(obj, list):
        return [complex_handler(item) for item in obj]
    else:
        return str(obj) if obj is not None else None

def pretty_print(obj):
    # Determine the type of the object and format accordingly
    if getattr(obj, 'object', '') == 'assistant':
        formatted_obj = {
            "id": getattr(obj, 'id', None),
            "object": getattr(obj, 'object', None),
            "created_at": getattr(obj, 'created_at', None),
            "description": getattr(obj, 'description', None),
            "file_ids": getattr(obj, 'file_ids', None),
            "instructions": getattr(obj, 'instructions', None),
            "metadata": getattr(obj, 'metadata', None),
            "model": getattr(obj, 'model', None),
            "name": getattr(obj, 'name', None),
            "tools": [tool.__dict__ for tool in getattr(obj, 'tools', [])]
        }
    elif getattr(obj, 'object', '') == 'thread':
        formatted_obj = {
            "id": getattr(obj, 'id', None),
            "object": getattr(obj, 'object', None),
            "created_at": getattr(obj, 'created_at', None),
            "metadata": getattr(obj, 'metadata', None)
        }
    elif getattr(obj, 'object', '') == 'thread.message':
        content = getattr(obj, 'content', [])
        formatted_content = []
        for c in content:
            formatted_content.append({
                "type": getattr(c, 'type', None),
                "text": {
                    "value": getattr(c.text, 'value', None),
                    "annotations": getattr(c.text, 'annotations', None)
                }
            })
        formatted_obj = {
            "id": getattr(obj, 'id', None),
            "object": getattr(obj, 'object', None),
            "created_at": getattr(obj, 'created_at', None),
            "thread_id": getattr(obj, 'thread_id', None),
            "role": getattr(obj, 'role', None),
            "content": formatted_content,
            "file_ids": getattr(obj, 'file_ids', None),
            "assistant_id": getattr(obj, 'assistant_id', None),
            "run_id": getattr(obj, 'run_id', None),
            "metadata": getattr(obj, 'metadata', None)
        },
    elif getattr(obj, 'object', '') == 'thread.run':
        # Formatting for Run object
        formatted_obj = {
            "id": getattr(obj, 'id', None),
            "assistant_id": getattr(obj, 'assistant_id', None),
            "cancelled_at": getattr(obj, 'cancelled_at', None),
            "completed_at": getattr(obj, 'completed_at', None),
            "created_at": getattr(obj, 'created_at', None),
            "expires_at": getattr(obj, 'expires_at', None),
            "failed_at": getattr(obj, 'failed_at', None),
            "file_ids": getattr(obj, 'file_ids', None),
            "instructions": getattr(obj, 'instructions', None),
            "last_error": getattr(obj, 'last_error', None),
            "metadata": getattr(obj, 'metadata', None),
            "model": getattr(obj, 'model', None),
            "object": getattr(obj, 'object', None),
            "required_action": complex_handler(getattr(obj, 'required_action', None)),
            "started_at": getattr(obj, 'started_at', None),
            "status": getattr(obj, 'status', None),
            "thread_id": getattr(obj, 'thread_id', None),
            "tools": [complex_handler(tool) for tool in getattr(obj, 'tools', [])]
        }
        
    else:
        # Fallback for unknown object types
        formatted_obj = complex_handler(obj)
    

    # Convert to JSON and print, use str for non-serializable objects
    print(json.dumps(obj, indent=2, default=complex_handler))


# pretty print threads
def pretty_print_thread(thread_messages):
    def capture_pretty_print_output(obj):
        buffer = io.StringIO()
        current_stdout = sys.stdout
        sys.stdout = buffer

        pretty_print(obj)  

        sys.stdout = current_stdout
        captured_output = buffer.getvalue()
        buffer.close()

        return captured_output

    def format_thread_content(thread_content):
        formatted_output = ""
        for message_json in thread_content:
            message = json.loads(message_json)
            role = message.get("role", "").capitalize()
            content_list = message.get("content", [])
            message_text = ""
            if content_list:
                text_content = content_list[0].get("text", {})
                message_text = text_content.get("value", "")

            formatted_output += f'{role}: "{message_text}"\n'

        return formatted_output

    thread_content = []
    for message in thread_messages.data:
        captured_content = capture_pretty_print_output(message)
        thread_content.append(captured_content)

    thread_content.reverse()
    return format_thread_content(thread_content)

