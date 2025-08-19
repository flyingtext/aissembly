# Philosophy of Aissembly

## 1. Minimalism in Language
- Aissembly is designed with only **three fundamental functions**.  
- This mirrors the essence of CPU/GPU ISA (e.g., Load, Compute, Branch) as the minimal set of operations.  
- By removing unnecessary syntax and abstractions, Aissembly expresses all computation through the **smallest possible functional core**.  

## 2. Language = ISA = Chip
- Aissembly is not just a high-level language but a **meta-representation of the ISA itself**.  
- Each language function directly corresponds to a hardware instruction, minimizing the need for intermediate layers such as LLVM IR, PTX, or heavy runtime drivers.  
- This philosophy reduces the gap between **language → ISA → hardware**, ensuring both efficiency and simplicity.  

## 3. Heterogeneous Parallelism
- Aissembly unifies **CPU, GPU, and specialized accelerators** under the same minimal function set.  
- Developers no longer need separate programming models (e.g., CUDA for GPU, C for CPU).  
- Any function call in Aissembly can be dynamically mapped to the most suitable hardware resource.  

## 4. Static and JIT Compilation
- **Static compilation** provides predictable, optimized execution plans.  
- **JIT compilation** adapts to real-time workloads, enabling dynamic resource allocation and load balancing across heterogeneous cores.  
- Aissembly’s lightweight design makes JIT especially powerful, combining the efficiency of static execution with the adaptability of runtime optimization.  

## 5. Toward Dedicated Hardware
- The long-term vision is an **Aissembly-native chip**, where the language directly defines the ISA and the hardware itself.  
- This eliminates the need for heavy software stacks like CUDA, ROCm, or complex driver models.  
- The result: a **minimal, universal, self-optimizing computing platform**.  
