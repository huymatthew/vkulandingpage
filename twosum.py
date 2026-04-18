n, target = map(int, input().split())
nums = list(map(int, input().split()))
hmap = {}

for i in range(len(nums)):
    if nums[i] in hmap:
        print(hmap[nums[i]], i)
        break
    else:
        hmap[target - nums[i]] = i
