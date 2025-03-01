import torch
import torch.distributed as dist
import os
import torch.multiprocessing as mp


def setup_distributed(rank, world_size):
    """Initialize distributed training"""
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    os.environ["LOCAL_RANK"] = str(rank)
    os.environ["RANK"] = str(rank)
    os.environ["WORLD_SIZE"] = str(world_size)

    # Initialize process group
    dist.init_process_group(backend="nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def all_reduce_test(rank, world_size):
    setup_distributed(rank, world_size)
    for x in range(20):
        with torch.no_grad():
            # Create a random tensor of size (10, 1GB)
            tensor_size = 4 * 1024 * 1024 * 1024  # 10x1GB
            local_tensor = torch.randn(tensor_size, device=f'cuda:{rank}')

            print(f"Rank {rank} tensor shape: {local_tensor.shape}")

            # Perform all_reduce across all GPUs
            dist.all_reduce(local_tensor, op=dist.ReduceOp.SUM)

            # Optionally, verify result
            if rank == 0:
                print(f"Rank {rank} tensor after all_reduce: {local_tensor[:5]}")  # Just print first 5 elements for verification
            del local_tensor

if __name__ == "__main__":
    world_size = torch.cuda.device_count()
    mp.spawn(
        all_reduce_test,
        args=(world_size,),
        nprocs=world_size,
        join=True
    )