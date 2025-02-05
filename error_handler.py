class ErrorHandler:
    def __init__(self):
        self.retry_count = 3
        self.error_logs = []
        
    def handle_error(self, error, context):
        """统一错误处理"""
        self.error_logs.append({
            'error': str(error),
            'context': context,
            'timestamp': datetime.now()
        })
        
        if isinstance(error, NetworkError):
            return self.handle_network_error(error)
        elif isinstance(error, AuthError):
            return self.handle_auth_error(error) 