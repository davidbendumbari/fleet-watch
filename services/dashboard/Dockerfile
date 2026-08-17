FROM node:20-slim
WORKDIR /app
COPY services/dashboard/package*.json ./
RUN npm install
COPY services/dashboard/ .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]