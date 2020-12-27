import torch
from torch.utils.data import TensorDataset, ConcatDataset
from torch.utils.data.dataloader import DataLoader
from torch.nn.modules.loss import BCELoss
import torch.optim as optim
import satnet

POINT_FEATURE = 4
HIDDEN_FEATURE = 16
ACTION_SPACE = 4

to_tensor = lambda t: torch.tensor(t, dtype=torch.float32)

class Policy_Net(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.point_linear_1 = torch.nn.Linear(in_features=2, out_features=HIDDEN_FEATURE)
        self.final_sat = satnet.SATNet(HIDDEN_FEATURE*ACTION_SPACE + ACTION_SPACE, 16, 64)
        self.is_input = torch.cat([torch.tensor([1 for _ in range(HIDDEN_FEATURE*ACTION_SPACE)] + [0 for _ in range(ACTION_SPACE)], dtype=torch.int)])

    def forward(self, points, features):
        assert points.size()[0] == 1
        assert features.size()[0] == 1
        points_hidden_1 = torch.sigmoid(self.point_linear_1(points[0]))
        all_hidden = torch.sigmoid(torch.matmul(points_hidden_1.t(), features[0]))
        flatten_hidden = torch.flatten(all_hidden)
        v_i = torch.cat([flatten_hidden, torch.zeros(ACTION_SPACE)]).unsqueeze(0)
        v_o = self.final_sat(v_i, self.is_input.unsqueeze(0))
        return v_o[:,-ACTION_SPACE:]

class Action_Predictior:
    def __init__(self):
        self.net = Policy_Net()

    def fit(self, points, features, actions, n_epoch=50000, lr=5e-4, batch_size=150):
        datasets = []
        optimizer = optim.Adam(params=self.net.parameters(), lr=lr)
        bceLoss = BCELoss()
        for p, f, a in zip(points, features, actions):
            one_set = TensorDataset(to_tensor(p[:-1]), to_tensor(f[:-1]), to_tensor(a))
            datasets.append(one_set)
        train_loader = DataLoader(ConcatDataset(datasets[:-1]), batch_size=1, shuffle=True)
        test_loader = DataLoader(ConcatDataset(datasets[-1:]), batch_size=1, shuffle=False)
        print(len(train_loader), len(test_loader))
        for e in range(n_epoch):
            print(f"Epoch: {e}")
            for i, (p, f, a) in enumerate(train_loader):
                out = self.net(p, f)
                loss = bceLoss(out, a)
                loss.backward()
                if i % batch_size == 0:
                    optimizer.step()
                    optimizer.zero_grad()

            sum_loss = 0
            with torch.no_grad():
                for i, (p, f, a) in enumerate(train_loader):
                    out = self.net(p, f)
                    loss = bceLoss(out, a)
                    sum_loss += loss
            sum_loss /= len(train_loader)
            print(f"Train Loss: {sum_loss.item()}")

            sum_loss = 0
            with torch.no_grad():
                for i, (p, f, a) in enumerate(test_loader):
                    out = self.net(p, f)
                    loss = bceLoss(out, a)
                    sum_loss += loss
            sum_loss /= len(test_loader)
            print(f"Test Loss: {sum_loss.item()}")
