    # How to Register Users

There are several ways to register users in the system:

## Method 1: Using FastAPI Interactive Docs (Easiest)

1. Open your browser and go to: `http://localhost:8000/docs`
2. Find the `/api/auth/register` endpoint
3. Click "Try it out"
4. Enter the request body:
   ```json
   {
     "roll_no": "RA123456",
     "dob": "2000-01-15"
   }
   ```
5. Click "Execute"
6. You'll see the response confirming the user was registered

## Method 2: Using cURL Command

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "roll_no": "RA123456",
    "dob": "2000-01-15"
  }'
```

## Method 3: Using Python Script

Create a file `register_user.py`:

```python
import requests

url = "http://localhost:8000/api/auth/register"
data = {
    "roll_no": "RA123456",
    "dob": "2000-01-15"
}

response = requests.post(url, json=data)
print(response.json())
```

Run it:
```bash
python register_user.py
```

## Method 4: Direct Database Insert (Advanced)

If you have many users to register, you can insert directly into the database:

```sql
INSERT INTO users (roll_no, dob) 
VALUES 
  ('RA123456', '2000-01-15'),
  ('RA123457', '2000-02-20'),
  ('RA123458', '2000-03-25');
```

## Important Notes

- **Date Format**: Always use `YYYY-MM-DD` format (e.g., `2000-01-15`)
- **Roll Number**: Will be automatically converted to uppercase
- **Duplicate Check**: If a roll number already exists, registration will fail
- **After Registration**: Users can immediately log in using the registered credentials

## Example Registration

```bash
# Register a user
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"roll_no": "RA123456", "dob": "2000-01-15"}'

# Response:
# {
#   "success": true,
#   "message": "User registered successfully",
#   "user_id": "uuid-here",
#   "roll_no": "RA123456"
# }
```

Then the user can log in at `http://localhost:5173` with:
- Roll Number: `RA123456`
- Date of Birth: `2000-01-15`

