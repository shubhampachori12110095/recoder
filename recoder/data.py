from torch.utils.data import Dataset

import numpy as np

import collections


__Interaction = collections.namedtuple('__Interaction', ['item_id', 'inter'])

class Interaction(__Interaction):
  pass


class RecommendationDataset(Dataset):

  def __init__(self, data=None, target_dataset=None,
               user_col='user', item_col='item', inter_col='inter'):

    self.data = data

    self.user_col = user_col
    self.item_col = item_col
    self.inter_col = inter_col
    self.target_dataset = target_dataset # type: RecommendationDataset

    self.index_col = self.user_col
    self.target_col = self.item_col

    self.__load_data()

  def __load_data(self):
    self.users = self.data[self.user_col].unique().tolist()
    self.items = self.data[self.item_col].unique().tolist()

    if self.target_dataset is not None:
      self.users = list(set(self.users + self.target_dataset.users))
      self.items = list(set(self.items + self.target_dataset.items))

    _grouped_data_df = self.data.groupby(by=self.index_col)

    if self.target_dataset is None:
      self.__groups = list(_grouped_data_df.groups.keys())
    else:
      _groups = list(_grouped_data_df.groups.keys())
      # to avoid having groups not in the target dataset
      self.__groups = list(np.intersect1d(_groups, self.target_dataset.__groups))

    self.__grouped_data = _grouped_data_df

  def __len__(self):
    return len(self.__groups)

  def __getitem__(self, index):
    _group = self.__groups[index]
    _data = self.__grouped_data.get_group(_group)

    interactions = []
    for item_id, inter in zip(_data[self.target_col], _data[self.inter_col]):
      interactions.append(Interaction(item_id=item_id, inter=inter))

    if self.target_dataset is None:
      _target_data = _data
      target_interactions = interactions
    else:
      _target_data = self.target_dataset.__grouped_data.get_group(_group)
      target_interactions = []
      for item_id, inter in zip(_target_data[self.target_col], _target_data[self.inter_col]):
        target_interactions.append(Interaction(item_id=item_id, inter=inter))

    return interactions, target_interactions
