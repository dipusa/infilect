## Instructions to Run this project locally

1. Login 
```
End point: api/v1/login/
Method: POST
Request Body:
        {
            "email": "dipa@gmail.com",
            "password": "1234"
        }
```
Note:
   After successful login you will  get access_token in the response pass this token in the 
   headers of each request in the following way
   ```
   "X-ACCESS-TOKEN": <your-token-value>
   ```

2. Craete a Group

```
End Point: api/v1/groups/
Method: POST
Request Body:
        {"name": "your group name"}
```

3. Get all groups created by logged in user

```
End Point: api/v1/groups/
Method: GET
```

4. Get photos belongs to a group(User either of the bellow end points)
```
End Point: api/v1/group/<group_id>
Method: GET
```

```
End Point: api/v1/photos/?group_id=<group_id>
Method: GET
```

5. Get details of a photo

```
End Point: api/v1/photos/<photo_id>
Method: GET
```

6. Logout

```
End Point: api/v1/logout/
Method: POST
```