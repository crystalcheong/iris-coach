#!/bin/bash

set -m

# Start the IRIS instance
iris start IRIS

# Unexpire user passwords
iris session iris -U%SYS '##class(Security.Users).UnExpireUserPasswords("*")'

# Run initializations and start services
iop --init
iop --migrate /irisdev/app/src/python/settings.py
iop --start Chat.Production --detach

# Start streamlit
streamlit run /irisdev/app/src/python/rag/🧑🏻‍⚕️_Chat.py --server.port=8051 --server.address=0.0.0.0

# Keep the IRIS instance running in the foreground
fg %1