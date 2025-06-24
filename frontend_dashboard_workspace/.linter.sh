#!/bin/bash
cd /home/kavia/workspace/code-generation/educonnect-portal-113568-0ff15646/frontend_dashboard_workspace/frontend_dashboard
npm run build
EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
   exit 1
fi

