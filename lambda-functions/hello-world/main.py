import json
def handler(event, context):
  message = "Hello, world!!"
  print(message)
  return {
    'statusCode': 200,
    'body': json.dumps(message)
  }