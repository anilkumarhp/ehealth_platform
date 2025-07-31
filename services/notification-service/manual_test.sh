#!/bin/bash
echo "Testing Notification Service API"

# Set variables
BASE_URL="http://localhost:8004/api/v1"
USER_ID="test-user-123"
NOTIFICATION_ID="user_management:test-notif-123"

echo
echo "1. Creating a notification..."
curl -X POST $BASE_URL/notifications/ \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"test-notif-123\",\"service\":\"user_management\",\"type\":\"info\",\"title\":\"Test Notification\",\"message\":\"This is a test notification\",\"user_id\":\"$USER_ID\"}"

echo
echo "2. Getting user notifications..."
curl -X GET $BASE_URL/notifications/user/$USER_ID

echo
echo "3. Marking notification as read..."
curl -X PUT $BASE_URL/notifications/user/$USER_ID/$NOTIFICATION_ID/read

echo
echo "4. Getting user notifications again (should be marked as read)..."
curl -X GET $BASE_URL/notifications/user/$USER_ID

echo
echo "Manual testing completed!"