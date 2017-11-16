[![Build Status](https://travis-ci.org/gr1d99/shopping-list-api.svg?branch=challenge-3)](https://travis-ci.org/gr1d99/shopping-list-api)  [![Coverage Status](https://coveralls.io/repos/github/gr1d99/shopping-list-api/badge.svg?branch=challenge-3)](https://coveralls.io/github/gr1d99/shopping-list-api?branch=challenge-3)  [![Code Climate](https://codeclimate.com/github/gr1d99/shopping-list-api/badges/gpa.svg)](https://codeclimate.com/github/gr1d99/shopping-list-api) [![Issue Count](https://codeclimate.com/github/gr1d99/shopping-list-api/badges/issue_count.svg)](https://codeclimate.com/shopping-list-api) 

# shopping-list-api
A RESTful ai Flask powered web application that allows users to record and share things they want to spend money on and keeping track of their shopping lists 

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

## Demo
[Shoppinglist-api](https://shoppinglistapiapp.herokuapp.com)



## Authentication Endpoints.

1. **User Registration**

  * **URL**

    `/users/register`

  * **Method:**

    `POST`

  * **Data Format**

    `application/json`
  
  * **Required**

      * `username`
      * `email`
      * `password`
  

  * **Success Response:**

    * **Code:** 201 CREATED
    
    * **Content:** 
  
          {status :"success", message : "Account created, login with your email and password to get your access tokens" }
 
  * **Error Response:**
  
    * **Code:** 422 UNPROCESSABLE ENTITY
    
    * **Content:** 
       
          {
              "messages": {
                  "email": [
                    "Missing data for required field."
                  ],
                  "username": [
                    "Missing data for required field."
                  ],
                  "password": [
                    "Missing data for required field."
                  ]
              }
          }   
    OR
    * **Code:** 409 CONFLICT
   
    * **Content:** 
                 
          { error: "username exists" }
          { error: "email exists" 
 
 2. **Login User**
 
   * **URL**
   
     `/users/login`

   * **Method:**

     `POST`

   * **Data Format**

     `application/json`
  
   * **Required**

      * `username`
      * `email`
      * `password`
      
   * **Data Params**
   
      * `username`
      * `email`
      * `password`
  

  * **Success Response:**

      * **Code:** 200 OK
      
      * **Content:** 
  
            {
                status:"success", 
                message: "Logged in",
                auth_token: "XXXXXXXXXX.XXXXXXXXX",
                "refresh_token": "XXXXXXXX.XXXXXX"
            }
 
  * **Error Response:**
  
    * **Code:** 422 UNPROCESSABLE ENTITY
    
    * **Content:** 
       
          {
              "messages": {
                  "username": [
                    "Missing data for required field."
                  ],
                  "password": [
                    "Missing data for required field."
                  ]
              }
          }   
    
    OR
    
    * **Code**: 401 UNAUTHORIZED
    
    * **Content**: 
      
          {
            "status": "fail",
            "message": "Incorrect username or password"
          }
  
 3. **Logout User.**
 
    * **URL**
   
      `/users/logout`

    * **Method:**

      `DELETE`

    * **Data Format**

      `application/json`
  
   * **Required**

      * `auth_token`

   * **Success Response:**

      * **Code:** 200 OK
      
      * **Content:** 
  
            {
                status:"success", 
                message: "Successfully logged out"
            }
 
   * **Error Response:**
  
      * **Code:** 401 UNAUTHORIZED
      
      * **Content:** 
      
            { "message": "authorization header required" }
      
      OR
    
      * **Code:** 422 UNPROCESSABLE ENTITY
      
      * **Content:** 
       
            { "message": "invalid authorization header" }
            
 4. **Reset User Password.**
 
   * **URL**
   
     `/users/reset-password`

   * **Method:**

     `POST`

   * **Data Format**

     `application/json`
  
   * **Required**
      
     * `old_password`
     * `new_password`
     * `confirm`
      
   * **Data Params**
   
     * `username`
     * `email`
     * `old_password`
     * `new_password`
     * `confirm`
     
   * **Success Response:**

     * **Code:** 200 OK
      
     * **Content:** 
  
           {
                status:"success", 
                message: "Your password has been successfully changed"
           }
     
   * **Error Response**
   
     * **Code:** 401 UNAUTHORIZED
     
     * **Content:**
     
            { "message": "Incorrect old password provided" }
            { "message": "Passwords do not match" }
            { "message": "User not found, login and try again" }
            
     OR
     
     * **Code:** 422 UNPROCESSABLE ENTITY
     
     * **Content:** 
    
           { "old_password": [
                "Missing data for required field."
                ]
           }
    
           { "new_password": [
                "Missing data for required field."
                ]
           }
           
           { "new_password": [
                "Missing data for required field."
                ]
           }
      
 5. **Refresh Auth Token.**
 
   * **URL**
   
     `/users/logout`

   * **Method:**

     `POST`

   * **Data Format**

      `application/json`
  
   * **Required**

      * `refresh_token`
      
   * **Success Response:**

      * **Code:** 200 OK
      
      * **Content:** 
  
            {
                status:"success", 
                auth_token: "XXXXXXXXXX.XXXXXXXXXXXX"
            }
      
   * **Error Response:**
  
      * **Code:** 401 UNAUTHORIZED
      
      * **Content:** 
      
            { "message": "authorization header required" }
      
      OR
    
      * **Code:** 422 UNPROCESSABLE ENTITY
      
      * **Content:** 
       
            { "message": "invalid authorization header" }
            
 6. **User Detail.**
 
   * **URL**
   
     `/users`

   * **Method:**

     `GET`

   * **Data Format**

     `application/json`
  
   * **Required**

     * `auth_token`
      
   * **Success Response:**

     * **Code:** 200 OK
      
     * **Content:** 
     
       ```json
        {
          "data": {
            "username": "example",
            "id": 1,
            "date_joined": "2017-11-14 03:34:06",
            "email": "example@email.com",
            "updated": "2017-11-14 03:34:06"
          },
          "status": "success"
        }

       ```
       
   * **Error Response**
   
     * **Code:** 401 UNAUTHORIZED
     
     * **Content:** 
     
           { "message": "authorization header required" }
           
     OR
     
     * **Code:** 422 UNPROCESSABLE ENTITY
     
     * **Content:** 
   
           { "message": "invalid authorization header" }
        
 7. **Update User.**
 
   * **URL**
     
     `/users`
     
   * **Method:**
     
     `PUT`
     
   * **Data Format**
   
     `application/json`
     
   * **Required**
   
     * `auth_token`
     
   * **Data Params**
     
     * `username`
     * `email`
     
   * **Success Response:**
   
     * **Code:** 200 OK
     
     * **Content:** 
     
        ```json
        {
           "data": {
             "id": 2,
             "username": "string1",
             "email": "string1@gmail.com",
             "date_joined": "2017-11-14 03:34:06",
             "updated": "2017-11-15 03:15:26"
             },
         "message": "Account updated",
         "status": "success"
        }
        ```
        
     * **Code:** 304 NOT MODIFIED
     
   * **Error Response**
   
     * **Code:** 401 UNAUTHORIZED
     
     * **Content:** 
     
           { "message": "authorization header required" }
           
     OR
                      
     * **Code:** 409 CONFLICT
     
     * **Content:**
     
           { "message": "username exists" }
           { "message": "email exists" }
           
     OR
     
     * **Code:** 422 UNPROCESSABLE ENTITY
     
     * **Content:** 
   
           { "message": "invalid authorization header" }
 
 8. **Delete User**.
 
    
   * **URL**
     
     `/users`
     
   * **Method:**
     
     `DELETE`
     
   * **Data Format**
   
     `application/json`
     
   * **Required**
   
     * `auth_token`
     
   * **Success Response**
   
     * **Code:** 204 NO CONTENT
     
     
   * **Error Response**
   
     * **Code:** 401 UNAUTHORIZED
     
     * **Content:** 
     
           { "message": "authorization header required" }
   
     OR
     
     * **Code:** 422 UNPROCESSABLE ENTITY
     
     * **Content:** 
   
           { "message": "invalid authorization header" }
           
           
## Shoppinglist Endpoints.

1. **Retrieve All Shoppinglists**

 * **URL**
 
   `/shopping-lists`

 * **Method:**

   `GET`

 * **Data Format**

    `application/json`
 
 * **Query Params**
 
    * **Optional**
    
      * `limit=[integer]`
      * `page=[integer]`
      
 * **Success Response:**
 
    * **Code:** 200 OK
    
    * **Content** 
    
      ```json
      {
        "status": "success",
        "total_pages": 1,
        "message": {
          "shopping_lists": [
            {
                "description": "my shoppinglist",
                "id": 2,
                "is_active": true,
                "name": "breakfast"
            }
          ]
        }
      }

 * **Error Response**
 
    * **Code:** 401 UNAUTHORIZED
     
    * **Content:** 
     
          { "message": "authorization header required" }
   
     OR
     
    * **Code:** 422 UNPROCESSABLE ENTITY
     
    * **Content:** 
   
           { "message": "invalid authorization header" }
           
           
2. **Create Shoppinglist**

 * **URL**
 
   `/shopping-lists`

 * **Method:**

   `POST`

 * **Data Format**

    `application/json`
    
 * **Data Params**
 
   * **Required**
 
     * `name`
  
   * **Optional**

     * `description`
     
 * **Success Response**
 
   * **Code:** 200 OK
   
   * **Content** 
   
     ```json
         {
          "message": "Shopping list created",
          "status": "success",
          "data": {
            "id": 2,
            "name": "string",
            "created_on": "2017-11-15 18:23:19"
          }
         }
         
 * **Error Response**
 
   * **Code:** 401 UNAUTHORIZED
     
   * **Content:** 
     
         { "message": "authorization header required" }
         
   OR
     
   * **Code:** 422 UNPROCESSABLE ENTITY
     
   * **Content:** 
   
         { "message": "invalid authorization header" }

3. **Retrieve Shoppinglist.**

 * **URL**
 
   `/shopping-lists/{ shoppinglistId }`
   
 * **Method**
 
   `GET`
   
 * **Url Params**
 
   * **Required**
 
     * `shoppinglistId=[integer]`
   
 * **Success Response**
 
   * **Code:** 200 OK
   
   * **Content:** 
   
     ```json
     {
       "status": "success",
       "message": {
         "id": 2,
         "name": "string",
         "description": "string",
         "total_items": 0,
         "bought_items": 0,
         "items_not_bought": 0,
         "created_on": "2017-11-15 18:23:19",
         "updated_on": "2017-11-15 18:23:19"
         }
       }
   
 * **Error Response**
 
   * **Code:** 401 UNAUTHORIZED
     
   * **Content:** 
     
         { "message": "authorization header required" }
         
   OR         
         
   * **Code:** 404 NOT FOUND
     
   * **Content:** 
     
         { "message": "Shopping list not found" }
         
   OR
   
   * **Code:** 409 CONFLICT
     
   * **Content:** 
     
         { "message": "There exists a shoppinglist with the provided name exists, try again with a different name" }
         
   OR
     
   * **Code:** 422 UNPROCESSABLE ENTITY
     
   * **Content:** 
   
         { "message": "invalid authorization header" }
   
4. **Update Shoppinglist.**

 * **URL**
 
   `/shopping-lists/{ shoppinglistId }`
   
 * **Method**
 
   `PUT`
   
 * **Url Params**
 
   * **Required**
 
     * `shoppinglistId=[integer]`
   
 * **Success Response**
 
   * **Code:** 200 OK
   
   * **Content:** 
   
     ```json
            {
               "status": "success",
               "message": "Shopping list updated",
               "data": {
               "created_on": "2017-11-15 18:23:19",
               "is_active": true,
               "name": "new string",
               "updated_on": "2017-11-16 03:29:11"
               }
            }
       
  
 * **Error Response**
 
   * **Code:** 401 UNAUTHORIZED
     
   * **Content:** 
     
         { "message": "authorization header required" }
         
   OR         
         
   * **Code:** 404 NOT FOUND
     
   * **Content:** 
     
         { "message": "Shopping list not found" }
         
   OR
   
   * **Code:** 409 CONFLICT
     
   * **Content:** 
     
         { "message": "There exists a shoppinglist with the provided name exists, try again with a different name" }
         
   OR
     
   * **Code:** 422 UNPROCESSABLE ENTITY
     
   * **Content:** 
   
         { "message": "invalid authorization header" }
         
 