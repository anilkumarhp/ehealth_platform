FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install
RUN npm install -D tailwindcss postcss autoprefixer

# Copy the rest of the application
COPY . .

# Initialize Tailwind if needed
RUN npx tailwindcss init -p

# Create a .env file with the environment variables
RUN echo "VITE_API_URL=http://localhost:8000" > .env
RUN echo "VITE_NOTIFICATION_URL=http://localhost:8004" >> .env

# Expose the port
EXPOSE 3000

# Start the application
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]