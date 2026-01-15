const express = require('express');
const { runCode } = require('./runCode');
const app = express();
app.use(express.json());
app.listen(3000, ()=> {
    console.log('Server is running on port 3000');
});

app.post('/api/run', async (req, res) => {
    const { code, input } = req.body;
    
    const result = runCode({ code, input });
    
    res.json(result);
});


