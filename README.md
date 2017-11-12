[![Build Status](https://travis-ci.org/gr1d99/shopping-list-api.svg?branch=challenge-3)](https://travis-ci.org/gr1d99/shopping-list-api)  [![Coverage Status](https://coveralls.io/repos/github/gr1d99/shopping-list-api/badge.svg?branch=challenge-3)](https://coveralls.io/github/gr1d99/shopping-list-api?branch=challenge-3)  [![Code Climate](https://codeclimate.com/github/gr1d99/shopping-list-api/badges/gpa.svg)](https://codeclimate.com/github/gr1d99/shopping-list-api) [![Issue Count](https://codeclimate.com/github/gr1d99/shopping-list-api/badges/issue_count.svg)](https://codeclimate.com/shopping-list-api) 

# shopping-list-api
A Flask powered web application that allows users to record and share things they want to spend money on and keeping track of their shopping lists 

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
See deployment for notes on how to deploy the project on a live system.

### Prerequisites
- Python3 [Installation](https://www.python.org/downloads/)
- Flask [Installation](http://flask.pocoo.org/)
- Git [Installation](https://git-scm.com/downloads)

## usage

```json

swagger: '2.0'
info:
  version: '1.0'
  title: 'shoppinglist'
  description: 'allows users to record their shopping lists'

"securityDefinitions": {
  "Bearer": {
    "name": "Authorization",
    "type": "apiKey",
    "in": "header",
    }
}

"paths": {
  "/auth/register": {
    "post": {
      
      "tags": [
        "Auth"
        ],
        
      "summary": "Create user object",
      
      "description": "User details should be sent in json format only.",
      
      "consumes": [
        "application/json",
        ],
        
      "produces": [
        "application/json",
        ],
        
      "parameters": [
        {
          "in": "body",
          "name": "body",
          "description": "Created user object",
          "required": true,
          "schema": {
            "$ref": "#/definitions/User"
            }
          }
        ],
      
      "responses": {
        "201": {
          "description": "user account created"
          },
          
          "401": {
            "description": "authorization required"
          },
          
          "409": {
            "description": "username or email exists"
          },
          
          "422": {
            "description": "missing data"
          },
          
          "500": {
            "description": "server error"
            },
        }
        
      }
  },
  
  "/auth/login": {
    "post": {
      "tags": [
        "Auth"
        ],
        
      "summary": "Login user object",
      
      "description": "Takes username and password and returns access tokens: 'auth_token, refresh_token'",
      
      "operationId": "username",
      
      "consumes": [
        "application/json",
        ],
      
      "produces": [
        "application/json",
        ],
        
      "parameters": [
        {
          "in": "body",
          "name": "body",
          "description": "Created user object",
          "required": true,
          "schema": {
            "properties": {
              "username": {
                "type": "string"
                },
                
                "password": {
                  "type": "string"
                  },
                }
              }
            }
        ],
        
      "responses": {
        
        "200": {
          "description": "successful login",
          },
          
        "401": {
          "description": "username and password do not match",
          },
          
        "422": {
          "description": "missing data",
          },
          
        "500": {
          "description": "server error",
          },
        }
      }
  },
  
  "/auth/logout": {
    "delete": {
      "tags": [
        "Auth"
        ],
        
      "security": [
        "Bearer": [],
        ],
      
      "summary": "Blacklists user auth_token",
      
      "description": "Logs out user object by blacklisting user auth_token",
      
      "responses": {
        "200": {
          "description": "User object logged out"
          },
          
        "422": {
          "description": "Invalid auth token"
          },
          
        },
      },
    },
  
  "/auth/reset-password": {
    "post": {
      "tags": [
        "Auth",
        ],
      
      "consumes": [
        "application/json"
        ],
        
      "produces": [
        "application/json",
        ],
        
      "responses": {
        "200": {
          "description": "password changed successfully"
          },
          
        "422": {
          "description": "invalid or missing data"
          },
          
        },
      
      "summary": "Resets user object password",
      
      "parameters": [
        {
          "name": "body",
          "in": "body",
          "required": true,
          "schema": {
                  "properties": {
                    "username": {
                      "type": "string"
                      },
        
                    "email": {
                      "type": "string"
                      },
                      
                    "old_password": {
                      "type": "string"
                      },
                      
                    "new_password": {
                      "type": "string"
                      },
                      
                    "confirm": {
                      "type": "string"
                      },
                  }
                }
            },
        ],
      },
    },
    
  "/auth/users": {
    "get": {
      "tags": [
        "Auth",
        ],
        
      "summary": "Retrieve user object",
      
      "description": "Takes username and password and returns access tokens: 'auth_token, refresh_token'",
      
      "consumes": [
        "application/json",
        ],
      
      "produces": [
        "application/json",
        ],
        
      "security": [
        "Bearer": [],
          ],
        
      "responses": {
        "200": {
          "description": "successful operation",
          },
        
        "422": {
          "description": "Bad authorization header",
          },
        
        "500": {
          "description": "server error",
          },
        },
      },
      
    "put":{
      "consumes": [
        "application/json",
        ],
        
      "parameters": [
        {
          "in": "body",
          "name": "body",
          "description": "Update user account",
          "required": true,
          "schema": {
            "properties": {
              "username": {
                "type": "string"
                },
                
                "email": {
                  "type": "string"
                  },
              }
            }
          },
        ],
        
      "produces": [
        "application/json",
        ],
        
      "tags": [
        "Auth"
        ],
        
      "summary": "Updates user object",
      
      "responses": {
        
        "200": {
          "description": "successful update of user account"
          },
          
        "422": {
          "description": "Bad authorization header or invalid email",
          },
          
        "500": {
          "description": "server error",
          },
          
        },
        
      "security": [
        "Bearer": [],
          ],
      },
    
    "delete": {
      "tags": [
        "Auth"
        ],
        
      "summary": "deletes user object",
      
      "consumes": [
        "application/json",
        ],
        
      "produces": [
        "application/json",
        ],
        
      "responses": {
        "204": {
          "description": "User object deleted successfully"
          },
          
        "422": {
          "description": "Bad authorization header",
          },
        },
        
      "security": [
        "Bearer": [],
        ],
        
    },
  },
  
  "/shopping-lists": {
    "get": {
      "summary": "retrieve all shoppinglists",
      
      "tags": [
        "Shoppinglists",
        ],
        
      "parameters": [
        {
          "description": "number of results to produce",
          "name": "limit",
          "in": "query",
          "required": false,
          "type": "integer"
          },
          
        {
          "description": "page number",
          "name": "page",
          "in": "query",
          "required": false,
          "type": "integer",
          },
        ],
        
      "security": [
        "Bearer": [],
        ],
      
      "responses": {
        "200": {
          "description": "Successfully fetched all shopping lists"
          },
        },
      },
      
    "post": {
      "summary": "creates shoppinglist object",
      
      "tags": [
        "Shoppinglists",
        ],
        
      "parameters": [
        {
          "name": "body",
          "in": "body",
          "required": true,
          "schema": {
            "$ref": "#/definitions/ShoppingList"
            }
          },
        ],
        
      "responses": {
        "201": {
          "description": "shoppinglist created successfully",
          },
          
        "401": {
          "description": "Authorization header required"
          },
          
        "409": {
          "description": "shopping list already exists"
          },
          
        "422": {
          "description": "unprocessed header or missing shoppinglist name"
          },
          
        },
        
      "security": [
        "Bearer": [],
        ],
        
      },
    },
    
  "/shopping-lists/{ID}" :{
    "get": {
      "summary": "Retrieve a single shoppinglist object",
      
      "tags": [
        "Shoppinglists",
        ],
        
      "parameters": [
        {
          "name": "ID",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppinglist object ID",
          },
        ],
        
      "responses": {
        "200": {
          "description": "shoppinglist object retrieved"
          },
        
        "401": {
          "description": "missing authorization header"
          },
        
        "404": {
          "description": "shoppinglist object not found"
          },
        },
      
      "security": [
        "Bearer": [],
        ],
      }, # end of get.
      
    "put": {
      "summary": "update shoppinglist object",
      
      "tags": [
        "Shoppinglists",
        ],
      
      "parameters": [
        {
          "name": "ID",
          "in": "path",
          "type": "integer",
          "required": true,
          },
          
        {
          "name": "body",
          "in": "body",
          "required": false,
          "schema": {
            "properties": {
              "new_name": {
                "type": "string"
                }
              }
            }
          },
        ],
        
      "responses": {
        "200": {
          "description": "shoppinglist object updated"
          },
          
        "304": {
          "description": "shoppinglist object not modified"
          },
          
        "401": {
          "description": "missing authorization header"
          },
          
        "404": {
          "description": "shoppinglist object not found"
          },
          
        "409": {
          "description": "shoppinglist object exists",
          },
        },
        
      "security": [
        "Bearer": [],
        ],
        
      }, # end of put.
      
    "delete": {
      "tags": [
        "Shoppinglists",
        ],
        
      "summary": "deletes shoppinglist object",
      
      "parameters": [
        {
          "description": "shoppinglist object ID",
          "name": "ID",
          "in": "path",
          "type": "integer",
          "required": true,
          },
        ],
      
      "responses": {
        "204": {
          "description": "shoppinglist object deleted"
          },
          
        "404": {
          "description": "shoppinglist object not found"
          },
        },
      
      "security": [
        "Bearer": [],
        ],
        
      }, # end of delete.
    },
    
  "/shopping-lists/{shoppinglistId}/shopping-items": {
    "get": {
      "tags": [
        "Shoppinglists",
        ],
      
      "summary": "retrieve all shoppingitems objects",
      
      "parameters": [
        {
          "name": "shoppinglistId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppinglist object ID"
          },
          
        {
          "name": "limit",
          "in": "query",
          "required": false,
          "type": "integer",
          "description": "limit the number of shoppingitems objects"
          },
          
        {
          "name": "page",
          "in": "query",
          "required": false,
          "type": "integer",
          "description": "jump to page number according to the results returned"
          },
        ],
        
      "responses": {
        "200": {
          "description": "shoppingitems objects retrieved"
          },
        
        "401": {
          "description": "missing authorization header"
          },
          
        "404": {
          "description": "shoppinglist object not found"
          },
        },
        
      "security": [
        "Bearer": [],
        ],
      
      }, # end of get.
      
    "post": {
      "tags": [
        "Shoppinglists",
        ],
      
      "summary": "create shoppingitem object",
      
      "parameters": [
        {
          "name": "shoppinglistId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "ID of shoppinglist object",
          },
          
        {
          "name": "body",
          "in": "body",
          "required": true,
          "description": "details of shoppingitem object",
          "schema": {
            "$ref": "#/definitions/ShoppingItem",
            }
          },
        ],
        
      "responses": {
        "201": {
          "description": "shoppingitem object created"
          },
          
        "401": {
          "description": "missing authorization header"
          },
          
        "404": {
          "description": "shoppinglist object not found"
          },
          
        },
        
      "security": [
        "Bearer": [],
        ],
      }, # end of post
      
    },
    
  "/shopping-lists/{shoppinglistId}/shopping-items/{shoppingitemId}": {
    "get": {
      "summary": "retrieve single shoppingitem object",
      
      "tags": [
        "Shoppinglists",
        ],
        
      "parameters": [
        {
          "name": "shoppinglistId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppinglist object ID"
          },
        
        {
          "name": "shoppingitemId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppingitem object ID"
          },

        ],
        
      "responses": {
        "200": {
          "description": "shoppingitem object retrieved",
          },
          
        "401": {
          "description": "authorization header required"
          },
          
        "404": {
          "description": "shoppingitem object not found"
          },
        },
        
      "security": [
        "Bearer": [],
        ],
      },
      
    "put": {
      "tags": [
        "Shoppinglists"
        ],
        
      "summary": "update shoppingitem object",
      
      "parameters": [
        {
          "name": "shoppinglistId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppinglist object ID"
          },
        
        {
          "name": "shoppingitemId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppingitem object ID"
          },
          
        {
          "name": "body",
          "in": "body",
          "required": false,
          "schema": {
            "$ref": "#/definitions/ShoppingItem"
            }
          },
        ],
      
      "responses": {
        "200": {
          "description": "shoppingitem object updated"
          },
          
        "401": {
          "description": "Authorization header required"
          },
        
        "404": {
          "description": "shoppinglist or shoppingitem object not found"
          },
          
        },
        
      "security": [
        "Bearer": []
        ],
      },
      
    "delete": {
      "tags": [
        "Shoppinglists",
        ],
      
      "summary": "delete shoppingitem object",
      
      "parameters": [
        {
          "name": "shoppinglistId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppinglist object ID"
          },
        
        {
          "name": "shoppingitemId",
          "in": "path",
          "type": "integer",
          "required": true,
          "description": "shoppingitem object ID"
          },
        ],
      
      "responses": {
        "204": {
          "description": "shoppingitem object deleted"
          },
          
        "401": {
          "description": "authorization header required"
          },
          
        "404": {
          "description": "shoppinglist or shoppingitem object not found"
          },
        },
        
      "security": [
        "Bearer": [],
        ],
      },
    },
    
  "/shopping-lists/search": {
    "get": {
      "tags": [
        "Search",
        ],
        
      "summary": "search shoppinglists objects",
      
      "description": "search and retrieves shoppinglist objects that match the query keyword",
      
      "parameters": [
        {
          "name": "q",
          "in": "query",
          "required": true,
          "type": "string"
          },
        
        {
          "description": "number of results to produce",
          "name": "limit",
          "in": "query",
          "required": false,
          "type": "integer"
          },
          
        {
          "description": "page number",
          "name": "page",
          "in": "query",
          "required": false,
          "type": "integer",
          },
        ],
      
      "responses": {
        "200": {
          "description": "search results found"
          },
          
        "401": {
          "description": "authorization header required"
          },
        },
        
      "security": [
        "Bearer": [],
        ],
      },
    },
}

"definitions": {
    "User": {
      "properties": {
        "username": {
          "type": "string"
        },
        
        "email": {
          "type": "string"
        },
        "password": {
          "type": "string"
        }
      },
    },
    
    "ShoppingList": {
      "properties": {
        "name": {
          "type": "string"
          }
        }
      },
      
    "ShoppingItem": {
      "properties": {
        "name": {
          "type": "string"
          },
        
        "price": {
          "type": "number",
          "format": "double"
          },
          
        "bought": {
          "type": "boolean",
          },
        }
      },
          
  }
  
host: 8b4c91cf.ngrok.io
basePath: /api/v1
schemes:
  - http

```

