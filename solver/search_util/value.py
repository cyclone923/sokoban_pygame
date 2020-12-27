import torch
from torch.utils.data import TensorDataset, ConcatDataset
from torch.utils.data.dataloader import DataLoader
from torch.nn.modules.loss import MSELoss
import torch.optim as optim

POINT_FEATURE = 4
HIDDEN_FEATURE = 4

to_tensor = lambda t: torch.tensor(t, dtype=torch.float32)

class Value_Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.point_linear_1 = torch.nn.Linear(in_features=2, out_features=HIDDEN_FEATURE)
        self.final_linear = torch.nn.Linear(in_features=HIDDEN_FEATURE*POINT_FEATURE, out_features=1)

    def forward(self, points, features): # batch_size set to 1
        assert points.size()[0] == 1
        assert features.size()[0] == 1
        points_hidden_1 = torch.relu(self.point_linear_1(points[0]))
        all_hidden = torch.sigmoid(torch.matmul(points_hidden_1.t(), features[0]))
        flatten_hidden = torch.flatten(all_hidden)
        value = self.final_linear(flatten_hidden).unsqueeze(0)
        return value

class Value_Predictior:
    def __init__(self):
        self.net = Value_Net()

    def fit(self, points, features, scores, n_epoch=2000, lr=5e-3):
        datasets = []
        optimizer = optim.Adam(params=self.net.parameters(), lr=lr)
        mseLoss = MSELoss()
        for p, f, s in zip(points, features, scores):
            one_set = TensorDataset(to_tensor(p), to_tensor(f), to_tensor(s))
            datasets.append(one_set)
        train_loader = DataLoader(ConcatDataset(datasets[:-1]), batch_size=1, shuffle=True)
        test_loader = DataLoader(ConcatDataset(datasets[-1:]), batch_size=1, shuffle=False)
        for e in range(n_epoch):
            print(f"Epoch: {e}")
            for i, (p, f, s) in enumerate(train_loader):
                out = self.net(p, f)
                loss = mseLoss(out, s)
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

            sum_loss = 0
            with torch.no_grad():
                for i, (p,f,s) in enumerate(train_loader):
                    out = self.net(p, f)
                    loss = mseLoss(out, s)
                    sum_loss += loss
            sum_loss /= len(train_loader)
            print(f"Train Loss: {sum_loss.item()}")

            sum_loss = 0
            with torch.no_grad():
                for i, (p,f,s) in enumerate(test_loader):
                    out = self.net(p, f)
                    loss = mseLoss(out, s)
                    sum_loss += loss
            sum_loss /= len(test_loader)
            print(f"Test Loss: {sum_loss.item()}")




