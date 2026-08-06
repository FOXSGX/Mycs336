import torch


class Linear(torch.nn.Module):
    def __init__(self,in_features,out_features,device=None,dtype=None):
        super().__init__()
        std = (2/(in_features + out_features))**0.5
        self.weight = torch.empty((out_features,in_features),device=device,dtype=dtype)
        self.weight = torch.nn.Parameter(self.weight)
        torch.nn.init.trunc_normal_(self.weight,mean=0,std=std,a=-3*std,b=3*std)

    def forward(self,x):
        return x @ self.weight.T



class Embedding(torch.nn.Module):
    def __init__(self,num_embeddings,embedding_dim,device=None,dtype=None):
        super().__init__()
        self.weight = torch.empty((num_embeddings,embedding_dim),device=device,dtype=dtype)
        self.weight = torch.nn.Parameter(self.weight)
        torch.nn.init.trunc_normal_(self.weight,mean=0,std=1,a=-3,b=3)

    def forward(self,token_ids):
        return self.weight[token_ids]


class RMSNorm(torch.nn.Module):
    def __init__(self,d_model,eps=1e-5,device=None,dtype=None):
        super().__init__()
        self.eps = eps
        self.weight = torch.ones((d_model,),device=device,dtype=dtype)
        self.weight = torch.nn.Parameter(self.weight)

    def forward(self,x):
        dtype = x.dtype
        x = x.to(torch.float32)
        z = torch.mean(x**2,dim=-1,keepdim=True)+self.eps
        scale = torch.rsqrt(z)
        return (x*scale*self.weight).to(dtype)
