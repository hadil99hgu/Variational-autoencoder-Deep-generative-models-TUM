import torch
import torch.nn as nn
import torch.nn.functional as F

from typeguard import typechecked
from torchtyping import TensorType, patch_typeguard
from typing import Tuple

from .decoder import Decoder
from .encoder import Encoder

patch_typeguard()

class VAE(nn.Module):
    def __init__(self, input_dim: int, latent_dim: int, hidden_dim: int=100):
        """Initialize the VAE model.
        
        Args:
            obs_dim (int): Dimension of the observed data x, int
            latent_dim (int): Dimension of the latent variable z, int
            hidden_dim (int): Hidden dimension of the encoder/decoder networks, int
        """
        super().__init__()
        self.latent_dim = latent_dim
        self.encoder = Encoder(input_dim, latent_dim, hidden_dim=hidden_dim)
        self.decoder = Decoder(input_dim, latent_dim, hidden_dim=hidden_dim)
    
    @typechecked
    def sample_with_reparametrization(self, mu: TensorType['batch_size', 'latent_dim'], 
                                      logsigma: TensorType['batch_size', 'latent_dim']) -> TensorType['batch_size', 'latent_dim']:
        """Draw sample from q(z) with reparametrization.
        
        We draw a single sample z_i for each data point x_i.
        
        Args:
            mu: Means of q(z) for the batch, shape [batch_size, latent_dim]
            logsigma: Log-sigmas of q(z) for the batch, shape [batch_size, latent_dim]
        
        Returns:
            z: Latent variables samples from q(z), shape [batch_size, latent_dim]
        """
        ##########################################################
        epsilon = torch.randn_like(mu)  # Sample from N(0, 1)
        sigma = torch.exp(logsigma)  # Calculate the standard deviations from the log-sigmas
        z = mu + epsilon * sigma  # Reparametrization trick: z = mu + epsilon * sigma
        return z
        ##########################################################
    
    @typechecked
    def kl_divergence(self, mu: TensorType['batch_size', 'latent_dim'], logsigma: TensorType['batch_size', 'latent_dim']) -> TensorType['batch_size']:
        """Compute KL divergence KL(q_i(z)||p(z)) for each q_i in the batch.
        
        Args:
            mu: Means of the q_i distributions, shape [batch_size, latent_dim]
            logsigma: Logarithm of standard deviations of the q_i distributions,
                      shape [batch_size, latent_dim]
        
        Returns:
            kl: KL divergence for each of the q_i distributions, shape [batch_size]
        """
        #########################################################
        kl = -0.5 * torch.sum(1 + 2 * logsigma - mu.pow(2) - (2 * logsigma).exp(), dim=1)
        #kl = -0.5 * torch.sum(1 + logsigma.pow(2) - mu.pow(2) - (logsigma.pow(2)).exp(), dim=1)
        return kl
        ##########################################################
    
    @typechecked
    def elbo(self, x: TensorType['batch_size', 'input_dim']) -> TensorType['batch_size']:
        """Estimate the ELBO for the mini-batch of data.
        
        Args:
            x: Mini-batch of the observations, shape [batch_size, input_dim]
        
        Returns:
            elbo_mc: MC estimate of ELBO for each sample in the mini-batch, shape [batch_size]
        """
        ##########################################################


        # Encode the input data to obtain the parameters of the variational distribution
        mu, logsigma = self.encoder(x)
        
        # Sample from the variational distribution using the reparametrization trick
        z = self.sample_with_reparametrization(mu, logsigma)

        # Decode the samples to obtain the parameters of the conditional likelihood
        theta = self.decoder(z)

        # Compute the reconstruction loss
        reconstruction_loss = torch.sum(x * torch.log(theta) + (1 - x) * torch.log(1 - theta), dim=1)

        # Compute the KL divergence
        kl_divergence = self.kl_divergence(mu, logsigma)

        # Compute the ELBO
        elbo_mc = reconstruction_loss - kl_divergence         
    
        return elbo_mc

        ##########################################################
        
    @typechecked
    def sample(self, num_samples: int, device: str='cpu') -> Tuple[
        TensorType['num_samples', 'latent_dim'],
        TensorType['num_samples', 'input_dim'],
        TensorType['num_samples', 'input_dim']]:
        """Generate new samples from the model.
        
        Args:
            num_samples: Number of samples to generate.
        
        Returns:
            z: Sampled latent codes, shape [num_samples, latent_dim]
            theta: Parameters of the output distribution, shape [num_samples, input_dim]
            x: Corresponding samples generated by the model, shape [num_samples, input_dim]
        """
        ##########################################################
         # Generate random samples from the latent space
        z = torch.randn(num_samples, self.latent_dim).to(device)

        # Generate samples from the decoder
        theta = self.decoder(z)

        # Sample from the output distribution
        x = torch.bernoulli(theta)

        return z, theta, x
        ##########################################################