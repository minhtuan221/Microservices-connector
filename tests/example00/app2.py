from microservices_connector.Interservices import Friend

aFriend= Friend('app1', 'http://0.0.0.0:5000')
message = aFriend.send('/helloworld','Mr. Developer')
print(message)
