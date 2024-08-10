import os
import json
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from typing import Dict, Any, Union


class TemplateRenderer:
    @staticmethod
    def render_template(template_dir: str, template_path: str, modifications: Dict[str, Any], format_type: str) -> Union[Dict, str]:
        try:
            env = TemplateRenderer._create_environment(template_dir)
            template = TemplateRenderer._load_template(env, template_path)
            rendered_body: str = template.render(modifications)
            format_body = TemplateRenderer._format_rendered_body(rendered_body, format_type)
            return format_body
        except (TemplateNotFound, json.JSONDecodeError) as e:
            raise ValueError(f"TemplateRenderer: Error rendering template: {str(e)}")
        except Exception as e:
            raise ValueError(f"TemplateRenderer: An unexpected error occurred while rendering template: {str(e)}")

    @staticmethod
    def _create_environment(template_dir: str) -> Environment:
        env = Environment(loader=FileSystemLoader(template_dir))
        env.filters['json_bool'] = lambda value: str(value).lower()
        return env

    @staticmethod
    def _load_template(env: Environment, template_path: str):
        template_name: str = os.path.basename(template_path)
        return env.get_template(template_name)

    @staticmethod
    def _format_rendered_body(rendered_body: str, format_type: str) -> Union[Dict, str]:
        if format_type == 'json':
            return json.loads(rendered_body)
        elif format_type == 'xml':
            return rendered_body
        else:
            raise ValueError(f"TemplateRenderer: Unsupported format type: {format_type}")
