from flask import jsonify, request
from flasgger import swag_from
from flask_restful import Resource
from application import db, api
from application.models import Conversation, Message

from model.model import response

class NewConversation(Resource):
    @swag_from({
        'responses': {
            200: {
                'description': 'Returns a new conversation UUID',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'uuid': {
                            'type': 'string',
                            'example': '123e4567-e89b-12d3-a456-426614174000'
                        }
                    }
                }
            }
        }
    })
    def post(self):
        """Create a new conversation and return its UUID"""
        # if not apikey:
        #     return {"error": "Missing API key"}, 401
        # if not ApiKey.check_api_key(apikey):
        #     return {"error": "Invalid API key"}, 401
        conversation = Conversation()
        db.session.add(conversation)
        db.session.commit()
        return jsonify({"uuid": str(conversation.uuid)})


class NewMessage(Resource):
    @swag_from({
        'parameters': [
            {
                'name': 'conversation_id',
                'in': 'json',
                'type': 'string',
                'required': True,
                'description': 'UUID of the conversation'
            },
            {
                'name': 'text',
                'in': 'json',
                'type': 'string',
                'required': True,
                'description': 'Text of the message'
            },
        ],
        'responses': {
            200: {
                'description': 'Response message',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'text': {
                            'type': 'string',
                            'example': 'Response for the message'
                        },
                        'images': {
                            'type': 'list',
                            'items': {
                                'type': 'string',
                                'example': 'image123.jpg'
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Conversation not found'
            }
        }
    })
    def post(self):
        """Add a new message to a conversation"""
        # if not apikey:
        #     return {"error": "Missing API key"}, 401
        # if not ApiKey.check_api_key(apikey):
        #     return {"error": "Invalid API key"}, 401
        data = request.get_json()
        conversation_id = data.get("conversation_id")
        text = data.get("text")
        conversation = Conversation.query.filter_by(uuid=conversation_id).first()
        if not conversation:
            return {"error": "Conversation not found"}, 404
        message = Message(text=text, author=0, conversation=conversation)
        answer, images, best_option = response(text, history=[])
        message2 = Message(text=answer, author=1, conversation=conversation)
        db.session.add(message)
        db.session.add(message2)
        db.session.commit()
        return jsonify({"text": answer, "images": images, "best_option": best_option})


class GetConversation(Resource):
    @swag_from({
        'parameters': [
            {
                'name': 'conversation_id',
                'in': 'json',
                'type': 'string',
                'required': True,
                'description': 'UUID of the conversation to retrieve messages from'
            }
        ],
        'responses': {
            200: {
                'description': 'List of all messages in the conversation',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'text': {'type': 'string', 'example': 'Hello, world!'},
                            'created': {'type': 'string', 'example': '2024-10-25T14:48:00.000Z'},
                            'author': {'type': 'boolean', 'example': True}
                        }
                    }
                }
            },
            404: {
                'description': 'Conversation not found'
            }
        }
    })
    def get(self):
        """Retrieve all messages from a conversation"""
        data = request.get_json()
        # if not apikey:
        #     return {"error": "Missing API key"}, 401
        # if not ApiKey.check_api_key(apikey):
        #     return {"error": "Invalid API key"}, 401
        conversation_id = data.get("conversation_id")
        conversation = Conversation.query.filter_by(uuid=conversation_id).first()
        if not conversation:
            return {"error": "Conversation not found"}, 404

        messages = [
            {
                "id": message.id,
                "text": message.text,
                "created": message.created.isoformat(),
                "author": message.author,
            }
            for message in conversation.messages
        ]
        return jsonify(messages)


# Registering routes
api.add_resource(NewConversation, '/new_conv')
api.add_resource(NewMessage, '/new_message')
api.add_resource(GetConversation, '/get_conv')
