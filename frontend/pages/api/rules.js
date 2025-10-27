export default async function handler(req, res) {
  if (req.method === 'POST') {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization,
        },
        body: JSON.stringify(req.body),
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
  } else if (req.method === 'GET') {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules`, {
        headers: { 
          'Authorization': req.headers.authorization 
        },
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
  } else if (req.method === 'PUT') {
    try {
      const { ruleId } = req.query;
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules/${ruleId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': req.headers.authorization,
        },
        body: JSON.stringify(req.body),
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
  } else if (req.method === 'DELETE') {
    try {
      const { ruleId } = req.query;
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/rules/${ruleId}`, {
        method: 'DELETE',
        headers: { 
          'Authorization': req.headers.authorization 
        },
      });
      
      if (response.ok) {
        res.status(200).json({ message: 'Rule deleted successfully' });
      } else {
        const data = await response.json();
        res.status(response.status).json(data);
      }
    } catch (error) {
      console.error('API Error:', error);
      res.status(500).json({ 
        error: 'Internal server error',
        detail: error.message 
      });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}
