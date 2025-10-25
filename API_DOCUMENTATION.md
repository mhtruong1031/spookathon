# API Documentation

## Overview
This API provides AI-powered image analysis for mathematical problems and graphs. It uses Google's Gemini AI model to analyze images and provide detailed explanations.

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required for current endpoints.

---

## Endpoints

### 1. Math Problem Explanation
**Endpoint:** `GET /math/explain`

**Description:** Analyzes an image to determine if it contains a math problem and provides a detailed explanation if it does.

**Input:**
- **Type:** `bytes` (image data)
- **Format:** Binary image data (JPEG, PNG, etc.)
- **Method:** GET request with image in request body

**Process:**
1. Validates if the image contains a math problem using AI
2. If it's a math problem, provides detailed explanation
3. If not a math problem, returns error message

**Response:**
- **Success (200):** 
  ```json
  "Detailed explanation of the math problem including the function behind the problem"
  ```
- **Error (200):** 
  ```json
  "This is not a math problem"
  ```

**Frontend Usage:**
```javascript
// Example frontend request
const formData = new FormData();
formData.append('image', imageFile);

fetch('/math/explain', {
  method: 'GET',
  body: formData
})
.then(response => response.text())
.then(explanation => console.log(explanation));
```

---

### 2. Graph Explanation
**Endpoint:** `GET /graph/explain`

**Description:** Analyzes an image to determine if it contains a graph (not a math problem) and provides detailed explanation of the graph's features.

**Input:**
- **Type:** `bytes` (image data)
- **Format:** Binary image data (JPEG, PNG, etc.)
- **Method:** GET request with image in request body

**Process:**
1. Validates if the image contains a math problem
2. If it's NOT a math problem (assumed to be a graph), provides graph explanation
3. If it is a math problem, returns error message

**Response:**
- **Success (200):** 
  ```json
  "Detailed explanation of the graph including critical points, direction changes, and educational context"
  ```
- **Error (200):** 
  ```json
  "This is a math problem"
  ```

**Frontend Usage:**
```javascript
// Example frontend request
const formData = new FormData();
formData.append('image', imageFile);

fetch('/graph/explain', {
  method: 'GET',
  body: formData
})
.then(response => response.text())
.then(explanation => console.log(explanation));
```



---

## Error Handling

### Common Error Scenarios:
1. **Invalid Image Format:** Ensure images are in supported formats (JPEG, PNG, etc.)
2. **Large Image Size:** Consider image compression for better performance
3. **AI Model Errors:** The API uses Google Gemini AI - ensure `GOOGLE_API_KEY` is properly configured

### Response Codes:
- **200:** Success (even for error messages like "This is not a math problem")
- **500:** Server error (check server logs)

---

## Frontend Integration Examples

### React Component Example:
```jsx
import React, { useState } from 'react';

const ImageAnalyzer = () => {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const analyzeImage = async (imageFile, type) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await fetch(`/${type}/explain`, {
        method: 'GET',
        body: formData
      });
      const explanation = await response.text();
      setResult(explanation);
    } catch (error) {
      setResult('Error analyzing image');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        accept="image/*" 
        onChange={(e) => {
          const file = e.target.files[0];
          if (file) {
            // Let user choose between math or graph analysis
            analyzeImage(file, 'math'); // or 'graph'
          }
        }}
      />
      {loading && <p>Analyzing...</p>}
      {result && <div>{result}</div>}
    </div>
  );
};
```

### JavaScript Fetch Example:
```javascript
// Analyze math problem
async function analyzeMathProblem(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch('/math/explain', {
    method: 'GET',
    body: formData
  });
  
  return await response.text();
}

// Analyze graph
async function analyzeGraph(imageFile) {
  const formData = new FormData();
  formData.append('image', imageFile);
  
  const response = await fetch('/graph/explain', {
    method: 'GET',
    body: formData
  });
  
  return await response.text();
}
```

---

## Technical Notes

### Image Requirements:
- **Supported Formats:** JPEG, PNG
- **Recommended Size:** Under 10MB for optimal performance
- **Quality:** Clear, well-lit images work best for AI analysis

### AI Model:
- Uses Google Gemini 2.5 Flash model
- Requires `GOOGLE_API_KEY` environment variable
- Processing time: 2-5 seconds typically

### Performance Considerations:
- First request may be slower due to model initialization
- Consider implementing loading states in frontend
- Image compression recommended for large files

---

## Development Setup

### Environment Variables Required:
```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### Running the Server:
```bash
cd server
python main.py
# or
uvicorn main:app --reload
```

### Testing Endpoints:
Use tools like Postman, curl, or the frontend to test:
```bash
curl -X GET "http://localhost:8000/math/explain" \
  -H "Content-Type: image/jpeg" \
  --data-binary @test_image.jpg
```
