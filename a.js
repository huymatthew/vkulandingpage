(async () => {
    // 1. Tải thư viện CCapture (bản nén)
    const loadScript = (url) => new Promise(r => {
        const s = document.createElement('script');
        s.src = url; s.onload = r; document.head.appendChild(s);
    });
    
    // Tải thư viện CCapture và encoder WebM
    await loadScript("https://raw.githack.com/spite/ccapture.js/master/build/CCapture.all.min.js");

    const canvas = document.getElementById('cvhuy');
    if (!canvas) return console.error("❌ Không thấy canvas 'cvhuy'");

    // 2. Khởi tạo CCapture
    const capturer = new CCapture({
        format: 'webm', // Xuất ra webm
        framerate: 30,  // Cố định 30fps
        verbose: true,
        display: true,  // Hiện bảng điều khiển trạng thái ở góc màn hình
        name: "cvhuy_record"
    });

    console.log("🚀 Bắt đầu quay... CCapture sẽ điều khiển thời gian của trang web.");
    
    // Bắt đầu quay
    capturer.start();

    // 3. Hàm loop để chụp từng frame
    let startTime = Date.now();
    const duration = 5000; // 5 giây

    function render() {
        const elapsed = Date.now() - startTime;
        
        if (elapsed < duration) {
            // Chụp frame hiện tại của canvas
            capturer.capture(canvas);
            requestAnimationFrame(render);
        } else {
            // Kết thúc và tải file
            console.log("📦 Đang xử lý video... Vui lòng đợi.");
            capturer.stop();
            capturer.save();
        }
    }

    render();
})();