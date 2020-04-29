import tensorflow as tf
class Encoder(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, encoder_units, batch_size):
        super(Encoder, self).__init__()
        self.batch_size = batch_size
        self.encoder_units = encoder_units
        self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
        self.gru = tf.keras.layers.GRU(self.encoder_units,
                                       return_sequences=True,
                                       return_state=True,
                                       recurrent_initializer='glorot_uniform')

    def call(self, x, hidden):
        x = self.embedding(x)
        output, state = self.gru(x, initial_state = hidden) #全部隐藏状态，最后一个隐藏状态
        return output, state

    def initialize_hidden_state(self):
        return tf.zeros((self.batch_size, self.encoder_units))


class Attention(tf.keras.layers.Layer):
	def __init__(self, units):
		super(Attention, self).__init__()
		self.W1 = tf.keras.layers.Dense(units)
		self.W2 = tf.keras.layers.Dense(units)
		self.V = tf.keras.layers.Dense(1)

	def call(self, query, values):
		hidden_with_the_time_axis = tf.expand_dims(query, 1)
		score = self.V(tf.nn.tanh(self.W1(values) +
								  self.W2(hidden_with_the_time_axis)))

		attention_weights = tf.nn.softmax(score, axis=1)

		context_vector = attention_weights * values
		context_vector = tf.reduce_sum(context_vector, axis=1)

		return context_vector, attention_weights


class Decoder(tf.keras.Model):
	def __init__(self, vocab_size, embedding_dim, decoder_units, batch_size):
		super(Decoder, self).__init__()
		self.batch_size = batch_size
		self.decoder_units = decoder_units
		self.embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim)
		self.gru = tf.keras.layers.GRU(self.decoder_units,
									   return_sequences=True,
									   return_state=True,
									   recurrent_initializer='glorot_uniform')
		self.fc = tf.keras.layers.Dense(vocab_size)
		self.attention = Attention(self.decoder_units)

	def call(self, x, hidden, encoder_output):
		context_vector, attention_weights = self.attention(hidden, encoder_output)
		x = self.embedding(x)
		x = tf.concat([tf.expand_dims(context_vector, 1), x], axis=-1)
		output, state = self.gru(x)

		output = tf.reshape(output, (-1, output.shape[2]))

		x = self.fc(output)

		return x, state, attention_weights
