curl https://one-api.glm.ai
curl https://172.18.196.246:3000 -X POST  \
     -H "Content-Type: application/json" \
     -d '{
           "stream": false,
           "inputs": "hello",
           "parameters": {
             "do_sample": false,
             "max_new_tokens": 128,
             "seed": 34,
             "details": true,
             "stop": ["<|endoftext|>", "<|user|>", "<|observation|>"],
             "return_full_text": false
           }
         }' \
    -x socks5h://127.0.0.1:8889