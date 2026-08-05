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
