```python
class Solution:
    def lengthOfLIS(self, nums: [int]) -> int:
        dp, res = [0] * len(nums), 0
        for num in nums:
            i, j = 0, res
            while i < j:
                m = (i + j) // 2
                if dp[m] < num: i = m + 1 # 如果要求非严格递增，将此行 '<' 改为 '<=' 即可。
                else: j = m
            dp[i] = num
            if j == res: 
                res += 1
        return res
```

```
dp = [1, 3, 5]
nums = 2

dp = [1, 2, 5]
nums = 3

dp = [1, 2, 3]

nums = 4
dp = [1, 2, 3, 4]

```