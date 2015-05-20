

from .fixed_length_message import FixedLengthMessage
from ...proto.server_pb2 import Response
from ...proto.client_pb2 import Request


class WallpServer(FixedLengthMessage):
	def __init__(self, server_shared_data):
		FixedLengthMessage.__init__(self)
		self._server_shared_data = server_shared_data


	def messageReceived(self, message):
		request = Request()
		request = request.ParseFromString(message)

		response = Response()

		wp_image = self._server_shared_data.wp_image
		wp_state = self._server_shared_data.wp_state

		print 'processing request..'
		print 'request type: ', request.type

		if request.type == Request.FREQUENCY:
			response.type = Response.FREQUENCY
			response.frequency.value = '1h'

		elif request.type == Request.LAST_CHANGE:
			response.type = Response.LAST_CHANGE
			response.last_change.timestamp = 0 #self._server_shared_data.last_change

		elif request.type == Request.IMAGE:
			if wp_state == WPState.READY:
				response.type = Response.IMAGE_INFO
				image_info = response.image_info

				image_info.extension = wp_image.extension
				image_info.length = wp_image.length
				image_info.chunk_count = wp_image.chunk_count

				self.transport.registerProducer(ImageChunksProducer(self.transport, wp_image))

			elif wp_state == WPState.CHANGING:
				response.type = Response.IMAGE_CHANGING

			elif wp_state == WPState.NONE:
				response.type = Response.IMAGE_NONE

			else:
				#log / handle error
				return


		else:
			response.type = Response.BAD_REQUEST

		self.sendMessage(response.SerializetoString())
