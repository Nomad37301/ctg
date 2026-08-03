FROM nginx:alpine

LABEL maintainer="TecArt CTF"
LABEL description="Web Challenge #1 — Source Code Inspection"

# Copy static challenge file
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
