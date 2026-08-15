from services.json_parser import parse_json_response


response = '{"name": "Python", "level": "beginner"}'

result = parse_json_response(response)

print(result)
try:
    parse_json_response('invalid json')
except ValueError as e:
    print(e)