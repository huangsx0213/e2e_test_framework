import json
from jinja2 import Environment, TemplateNotFound
from typing import Dict, Any, Union


class TemplateRenderer:
    @staticmethod
    def render_template(template_content, render_by: Dict[str, Any], format_type: str) -> Union[Dict, str]:
        try:
            env = TemplateRenderer._create_environment()
            template = env.from_string(template_content)
            rendered_body: str = template.render(render_by)
            format_body = TemplateRenderer._format_rendered_body(rendered_body, format_type)
            return format_body
        except (TemplateNotFound, json.JSONDecodeError) as e:
            raise ValueError(f"TemplateRenderer: Error rendering template: {str(e)}")
        except Exception as e:
            raise ValueError(f"TemplateRenderer: An unexpected error occurred while rendering template: {str(e)}")

    @staticmethod
    def _create_environment() -> Environment:
        env = Environment()
        env.filters['json_bool'] = lambda value: str(value).lower()
        return env

    @staticmethod
    def _format_rendered_body(rendered_body: str, format_type: str) -> Union[Dict, str]:
        if format_type == 'json':
            return json.loads(rendered_body)
        elif format_type == 'xml':
            return rendered_body
        else:
            raise ValueError(f"TemplateRenderer: Unsupported format type: {format_type}")
