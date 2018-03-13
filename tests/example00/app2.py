from microservices_connector.Interservices import Friend

F = Friend('app1', 'http://0.0.0.0:5000')
message = F.send('/helloworld','Mr. Developer')
print(message)
