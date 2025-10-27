export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { name, password } = req.body;
    
    if (!name || !password) {
      return res.status(400).json({ 
        error: 'Bad request',
        detail: 'Name and password are required' 
      });
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/tenants/login`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({ name, password }),
    });
    
    const data = await response.json();
    
    if (response.ok) {
      res.status(200).json(data);
    } else {
      res.status(response.status).json(data);
    }
  } catch (error) {
    console.error('API Error:', error);
    res.status(500).json({ 
      error: 'Internal server error',
      detail: error.message 
    });
  }
}
