#This is the project of the chapter "Variational Autoencoder" of teh course "Deep Generative Models" suggested by the technoical university of Munich.
The goal if this project is to impelement the Variational Autoencoder (VAE). The main idea is to augment an autoencoder architecture with probabilistic latent embeddings.
The autoencoder consists of two parts: An encoder that takes inputs and encodes them into a lower-dimensional manifold. The decoder than maps these embeddings back to the original inputs.
Thus, the latent embeddings of the encoder are ought to be compressed representations. In the VAE, the encoder instead outputs a latent (variational) distribution from which the latent embeddings
are sampled. This "smoothens" the latent space of the autoencoder and allows for example sampling new latent representations (i.e. generating new data) or interpolating between two latent embeddings 
(while the decoder still provides meaningful reconstructions).
