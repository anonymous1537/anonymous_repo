import numpy as np
import torch
from torch.utils.data import Dataset

class InMemoryDataset(torch.utils.data.Dataset):
    def __init__(self, source, transform=None, t_max=None, is_squeeze=False, is_unsqueeze=False):
        self.transform = transform
        self.t_max = t_max
        self.is_squeeze = is_squeeze
        self.is_unsqueeze = is_unsqueeze

        if type(source) == type(str()):
            self.samples = np.load(source)

        elif type(source) == type(np.array([])):
            self.samples = source

        else:
            print(f"ERROR: UNKNOWN DATA TYPE {type(source)}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index: int):
        sample = np.array(self.samples[index])

        #scaling
        sample = torch.from_numpy(
            (sample - sample.min())/(sample.max() - sample.min())
        ).to(torch.float32)

        if self.transform: sample = self.transform(sample)
        if self.is_squeeze: sample = sample.squeeze()
        if self.is_unsqueeze: sample = sample.unsqueeze(axis=-3)
        if self.t_max is not None: 
            if len(sample.shape) == 2:
                sample = sample[:, :self.t_max]
            elif len(sample.shape) == 3:
                sample = sample[:, :, :self.t_max]
            elif len(sample.shape) == 4:
                sample = sample[:, :, :, :self.t_max]
            else:
                raise NotImplementedError(f"Unexpected sample number of dimensions {len(sample.shape)}")
            
        return sample

    def random_shuffled_iterator(self, batch_size: int):
        while True:
            inds = torch.randint(0, len(self.samples), [batch_size])
            yield torch.stack([self.__getitem__(idx) for idx in inds])