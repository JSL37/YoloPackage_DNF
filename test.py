import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit

def build_engine(onnx_file_path, engine_file_path):
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)
    
    with open(onnx_file_path, 'rb') as model:
        if not parser.parse(model.read()):
            print('ERROR: Failed to parse the ONNX file.')
            for error in range(parser.num_errors):
                print(parser.get_error(error))
            return None
    
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30  # 1GB
    
    # 启用INT8量化
    if builder.platform_has_fast_int8:
        config.set_flag(trt.BuilderFlag.INT8)
    
    engine = builder.build_engine(network, config)
    
    with open(engine_file_path, 'wb') as f:
        f.write(engine.serialize())
    
    return engine

# 使用示例
build_engine('best.onnx', 'best.engine')