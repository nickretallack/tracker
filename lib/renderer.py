### TEMPLATE RENDERER
import jinja2
env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'), line_statement_prefix="#")

def render(template,**args):
  return env.get_template(template+'.html').render(**args)
  
from S3save import s3_get_url
env.filters['s3'] = s3_get_url
