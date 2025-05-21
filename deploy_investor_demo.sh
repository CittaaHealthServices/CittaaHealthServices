#!/bin/bash


docker build -t vocalysis-investor-demo .

docker run -d \
  --name vocalysis-investor-demo \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/model:/app/model \
  -e DB_TYPE=sqlite \
  -e ENCRYPTION_KEY=vocalysis_secure_encryption_key_for_investor_demo \
  vocalysis-investor-demo

echo "Vocalysis container started on port 8501"
echo "To expose the service with authentication, run:"
echo "streamlit tunnel --scope public --port 8501 --auth-username Cittaa2023 --auth-password Cittaa@Investors2024"
