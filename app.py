from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from detectors.enhanced_free_detector import EnhancedFreeDetector
from utils.db import IrisDB
from auth_service import AuthService

app = Flask(__name__)
CORS(app)

# Initialiseer services
iris_detector = EnhancedFreeDetector()
db = IrisDB()
auth_service = AuthService()

@app.route('/api/register-iris', methods=['POST'])
def register_iris():
    try:
        data = request.json
        user_id = data.get('user_id')
        image_data = data.get('image')
        
        # Decodeer afbeelding
        img_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process iris
        iris = iris_detector.detect_and_process(img)
        if iris is not None:
            features = iris_detector.extract_features(iris)
            db.add_iris(user_id, features)
            return jsonify({'success': True, 'message': 'Iris geregistreerd'})
            
        return jsonify({'success': False, 'message': 'Geen iris gedetecteerd'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/login-with-iris', methods=['POST'])
def login_with_iris():
    try:
        data = request.json
        image_data = data.get('image')
        
        # Decodeer afbeelding
        img_bytes = base64.b64decode(image_data.split(',')[1])
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Process iris
        iris = iris_detector.detect_and_process(img)
        if iris is None:
            return jsonify({'success': False, 'message': 'Geen iris gedetecteerd'})
            
        features = iris_detector.extract_features(iris)
        user_id = db.find_matching_iris(features)
        
        if user_id:
            token = auth_service.create_auth_token(user_id)
            return jsonify({
                'success': True,
                'token': token,
                'user_id': user_id
            })
            
        return jsonify({'success': False, 'message': 'Iris niet herkend'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
