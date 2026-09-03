




'''
if __name__ == '__main__':
    # Starts the local development server
    app.run(debug=True)
'''
if __name__ == '__main__':
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'), host='127.0.0.1', port=5000)
