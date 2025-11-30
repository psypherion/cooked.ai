# **API Contract \- Project "Cooked"**

Version: 1.0.0  
Status: Draft

## **Overview**

This document defines the communication protocol between the Next.js Frontend and the FastAPI Backend. All endpoints are prefixed with /api/v1.

## **1\. Endpoints**

### **Generate Roast**

Endpoint: POST /generate-roast  
Description: The core endpoint that takes user preferences (and optional image) and returns a structured, sarcastic roast.

#### **Request Headers**

|

| Header | Value | Required |  
| Content-Type | multipart/form-data | Yes (due to potential image upload) |

#### **Request Body (Form Data)**

| Field | Type | Required | Description |  
| name | string | Yes | The user's display name or handle. |  
| taste | string | Yes | Free text list of artists, movies, or hobbies. |  
| image | file | No | A JPEG/PNG image file (Selfie or Room photo) for visual analysis. |

#### **Response Body (JSON)**

**Code:** 200 OK
```
{  
  "status": "success",  
  "data": {  
    "user\_profile": {  
      "display\_name": "User Name",  
      "archetype": "The 'I was born in the wrong generation' Guy"  
    },  
    "roast": {  
      "headline": "Your taste is completely derivative.",  
      "music\_roast": "Listening to \[Artist Name\] in 2024 is practically a cry for help.",  
      "movie\_roast": "You listed \[Movie Name\] because you saw it on a 'Top 100' list, not because you understood it.",  
      "visual\_roast": "Your room looks like it smells of stale vape juice and regret. (Optional field)",  
      "overall\_verdict": "You are the human equivalent of unseasoned chicken."  
    },  
    "stats": {  
      "basic\_score": 85,  
      "red\_flag\_score": 12  
    },  
    "verdict": {  
      "verdict\_1": "Basic",  
      "verdict\_2": "No Taste",  
      "verdict\_3": "Trend Hopper",  
      "verdict\_4": "Boring"  
    }  
  }  
}
```


### **Error Responses**

#### **400 Bad Request**

Returned when required fields are missing.
```
{  
  "status": "error",  
  "code": "MISSING\_FIELDS",  
  "message": "Name and Taste fields are required."  
}
```
#### **429 Too Many Requests**

Returned if the user hits the API too frequently (Rate Limiting).

```
{  
  "status": "error",  
  "code": "RATE\_LIMIT\_EXCEEDED",  
  "message": "You are being roasted too hard. Cool off for a minute."  
}
```
#### **500 Internal Server Error**

Returned if the AI service fails or times out.

```
{  
  "status": "error",  
  "code": "AI\_GENERATION\_FAILED",  
  "message": "The AI refused to roast you. You might be too boring."  
}
```