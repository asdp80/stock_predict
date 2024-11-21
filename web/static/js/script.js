// // // 전역 변수로 차트 객체 관리
// // let predictionChart = null;
// //
// // async function predictStock(stockCode) {
// //     try {
// //         // 예측 데이터 가져오기
// //         const response = await fetch(`/api/predict/${stockCode}`);
// //         const data = await response.json();
// //
// //         if (data.error) {
// //             alert('예측 중 오류가 발생했습니다: ' + data.error);
// //             return;
// //         }
// //
// //         // 예측 상세 정보 표시
// //         document.getElementById('predictionDetails').innerHTML = `
// //             <p>현재 가격: ${data.current_price.toLocaleString()}원</p>
// //             <p>예측 방향: ${data.direction}</p>
// //             <p>예측 정확도: ${data.accuracy.toFixed(2)}%</p>
// //         `;
// //
// //         // 차트 생성 또는 업데이트
// //         const ctx = document.getElementById('predictionChart').getContext('2d');
// //
// //         // 기존 차트가 있다면 제거
// //         if (predictionChart) {
// //             predictionChart.destroy();
// //         }
// //
// //         // 새로운 차트 생성
// //         predictionChart = new Chart(ctx, {
// //             type: 'line',
// //             data: {
// //                 labels: Array.from({length: 7}, (_, i) => `${i + 1}일 후`),
// //                 datasets: [{
// //                     label: '예측 가격',
// //                     data: data.future_predictions,
// //                     borderColor: 'rgb(75, 192, 192)',
// //                     tension: 0.1
// //                 }]
// //             },
// //             options: {
// //                 responsive: true,
// //                 maintainAspectRatio: false,
// //                 plugins: {
// //                     legend: {
// //                         position: 'top',
// //                         labels: {
// //                             color: '#fff'  // 범례 텍스트 색상
// //                         }
// //                     }
// //                 },
// //                 scales: {
// //                     y: {
// //                         ticks: {
// //                             color: '#fff'  // Y축 텍스트 색상
// //                         },
// //                         grid: {
// //                             color: 'rgba(255, 255, 255, 0.1)'  // Y축 그리드 색상
// //                         }
// //                     },
// //                     x: {
// //                         ticks: {
// //                             color: '#fff'  // X축 텍스트 색상
// //                         },
// //                         grid: {
// //                             color: 'rgba(255, 255, 255, 0.1)'  // X축 그리드 색상
// //                         }
// //                     }
// //                 }
// //             }
// //         });
// //
// //
// //
// // // 모달 열기
// // function openModal() {
// //     document.getElementById('predictionModal').classList.remove('hidden');
// // }
// //
// // // 모달 닫기
// // function closeModal() {
// //     document.getElementById('predictionModal').classList.add('hidden');
// // }
// //
// // // 페이지가 로드될 때 초기화
// // document.addEventListener('DOMContentLoaded', () => {
// //     console.log('페이지가 로드되었습니다.');
// //     const canvasElement = document.getElementById('predictionChart');
// //     console.log(canvasElement);  // canvasElement가 실제 canvas인지 확인
// //     if (canvasElement) {
// //         const ctx = canvasElement.getContext('2d');
// //         console.log(ctx);  // 정상적으로 콘솔에 출력되어야 합니다.
// //     } else {
// //         console.error('예측 차트 캔버스를 찾을 수 없습니다.');
// //     }
// // });
// //
// // const canvasElement = document.getElementById('predictionChart');
// // console.log(canvasElement);  // <canvas id="predictionChart" ...>
// // const ctx = canvasElement.getContext('2d');
// // console.log(ctx);  // 정상적으로 콘솔에 출력되어야 합니다.
//
// // 전역 변수로 차트 객체 관리
// let predictionChart = null;
//
// async function predictStock(stockCode) {
//     try {
//         // 예측 데이터 가져오기
//         const response = await fetch(`/api/predict/${stockCode}`);
//         const data = await response.json();
//
//         if (data.error) {
//             alert('예측 중 오류가 발생했습니다: ' + data.error);
//             return;
//         }
//
//         // 예측 상세 정보 표시
//         const detailsHtml = `
//             <div class="mb-6 text-lg">
//                 <div class="grid grid-cols-2 gap-4 mb-4">
//                     <div class="bg-gray-700 p-4 rounded">
//                         <p class="font-bold mb-2">현재 가격</p>
//                         <p class="text-xl">${data.current_price.toLocaleString()}원</p>
//                     </div>
//                     <div class="bg-gray-700 p-4 rounded">
//                         <p class="font-bold mb-2">예측 방향</p>
//                         <p class="text-xl ${data.direction === '상승' ? 'text-green-500' : 'text-red-500'}">${data.direction}</p>
//                     </div>
//                 </div>
//                 <div class="bg-gray-700 p-4 rounded">
//                     <p class="font-bold mb-2">예측 정확도</p>
//                     <p class="text-xl">${data.accuracy.toFixed(2)}%</p>
//                 </div>
//             </div>
//             <div class="mb-6">
//                 <h3 class="text-xl font-bold mb-4">최근 예측 결과</h3>
//                 <div class="overflow-x-auto">
//                     <table class="w-full text-sm">
//                         <thead>
//                             <tr class="bg-gray-700">
//                                 <th class="p-2">날짜</th>
//                                 <th class="p-2">실제 가격</th>
//                                 <th class="p-2">예측 가격</th>
//                             </tr>
//                         </thead>
//                         <tbody>
//                             ${data.recent_predictions.map(pred => `
//                                 <tr class="border-b border-gray-700">
//                                     <td class="p-2">${pred.date}</td>
//                                     <td class="p-2">${pred.actual.toLocaleString()}원</td>
//                                     <td class="p-2">${pred.predicted.toLocaleString()}원</td>
//                                 </tr>
//                             `).join('')}
//                         </tbody>
//                     </table>
//                 </div>
//             </div>
//             <p class="text-sm text-gray-400 mt-4">* 주가 예측은 참고용이며, 투자의 책임은 투자자 본인에게 있습니다.</p>
//         `;
//
//         document.getElementById('predictionDetails').innerHTML = detailsHtml;
//
//         // 차트 생성 또는 업데이트
//         const ctx = document.getElementById('predictionChart').getContext('2d');
//
//         // 기존 차트가 있다면 제거
//         if (predictionChart) {
//             predictionChart.destroy();
//         }
//
//         // 새로운 차트 생성
//         predictionChart = new Chart(ctx, {
//             type: 'line',
//             data: {
//                 labels: data.dates,
//                 datasets: [{
//                     label: '실제 가격',
//                     data: data.actual_prices,
//                     borderColor: 'rgb(75, 192, 192)',
//                     tension: 0.1
//                 }, {
//                     label: '예측 가격',
//                     data: data.predicted_prices,
//                     borderColor: 'rgb(255, 99, 132)',
//                     tension: 0.1
//                 }]
//             },
//             options: {
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 plugins: {
//                     legend: {
//                         position: 'top',
//                         labels: { color: '#fff' }
//                     },
//                     tooltip: {
//                         mode: 'index',
//                         intersect: false
//                     }
//                 },
//                 scales: {
//                     y: {
//                         ticks: { color: '#fff' },
//                         grid: { color: 'rgba(255, 255, 255, 0.1)' }
//                     },
//                     x: {
//                         ticks: { color: '#fff' },
//                         grid: { color: 'rgba(255, 255, 255, 0.1)' }
//                     }
//                 }
//             }
//         });
//
//         // 모달 표시
//         const modal = document.getElementById('predictionModal');
//         modal.classList.remove('hidden');
//         modal.classList.add('flex');  // Flexbox 적용
//
//     } catch (error) {
//         console.error('예측 요청 중 오류:', error);
//         alert('예측 요청 중 오류가 발생했습니다: ' + error.message);
//     }
// }
//
// // 모달 닫기 함수
// function closeModal() {
//     const modal = document.getElementById('predictionModal');
//     modal.classList.add('hidden');
//     modal.classList.remove('flex');
// }
//
// // ESC 키로 모달 닫기
// document.addEventListener('keydown', (e) => {
//     if (e.key === 'Escape') {
//         closeModal();
//     }
// });
//
// // 모달 외부 클릭 시 닫기
// document.addEventListener('click', (e) => {
//     const modal = document.getElementById('predictionModal');
//     if (e.target === modal) {
//         closeModal();
//     }
// });

async function predictStock(stockCode) {
    try {
        // 로딩 모달 표시
        const loadingModal = document.getElementById('loadingModal');
        loadingModal.classList.remove('hidden');
        loadingModal.classList.add('flex');

        // 기존 예측 모달 숨기기
        const predictionModal = document.getElementById('predictionModal');
        predictionModal.classList.add('hidden');
        predictionModal.classList.remove('flex');

        // API 호출
        const response = await fetch(`/api/predict/${stockCode}`, {
            headers: {
                'Accept': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // 로딩 모달 숨기기
        loadingModal.classList.add('hidden');
        loadingModal.classList.remove('flex');

        // 데이터 업데이트
        updatePredictionDetails(data);
        updatePredictionChart(data);

        // 결과 모달 표시
        predictionModal.classList.remove('hidden');
        predictionModal.classList.add('flex');

    } catch (error) {
        console.error('예측 요청 중 오류:', error);

        // 로딩 모달 숨기기
        loadingModal.classList.add('hidden');

        // 에러 메시지 표시
        alert('예측 중 오류가 발생했습니다: ' + error.message);
    }
}

// 모달 닫기 함수 수정
function closeModal() {
    document.getElementById('predictionModal').classList.add('hidden');
    document.getElementById('loadingModal').classList.add('hidden');
}

// 차트 업데이트 함수
function updatePredictionChart(data) {
    const ctx = document.getElementById('predictionChart').getContext('2d');

    if (predictionChart) {
        predictionChart.destroy();
    }

    // 날짜 데이터 준비
    const allDates = [
        ...data.dates,
        ...Array.from({length: 7}, (_, i) => `D+${i+1}`)
    ];

    // 실제 가격과 예측 가격 데이터 준비
    const actualPrices = [
        ...data.actual_prices,
        ...Array(7).fill(null)
    ];

    const predictedPrices = [
        ...data.predicted_prices,
        ...data.future_predictions
    ];

    predictionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allDates,
            datasets: [{
                label: '실제 가격',
                data: actualPrices,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1,
                pointRadius: 3
            }, {
                label: '예측 가격',
                data: predictedPrices,
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#fff' }
                },
                tooltip: {
                    enabled: true,
                    callbacks: {
                         label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += Math.round(context.parsed.y).toLocaleString() + '원';
                        }
                        return label;
                        }
                    }
                }
            },
             scales: {
            y: {
                ticks: {
                    color: '#fff',
                    callback: function(value) {
                        return Math.round(value).toLocaleString() + '원';
                    }
                },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            },
            x: {
                ticks: { color: '#fff' },
                grid: { color: 'rgba(255, 255, 255, 0.1)' }
            }

            }
        }
    });
}

// 예측 상세 정보 업데이트 함수
function updatePredictionDetails(data) {
    document.getElementById('predictionDetails').innerHTML = `
        <div class="grid grid-cols-2 gap-4 mb-6">
            <div class="bg-gray-700 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">현재 가격</h3>
                <p class="text-2xl">${Math.round(data.current_price).toLocaleString()}원</p>
            </div>
            <div class="bg-gray-700 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">예측 방향</h3>
                <p class="text-2xl ${data.direction === '상승' ? 'text-green-500' : 'text-red-500'}">${data.direction}</p>
            </div>
            <div class="bg-gray-700 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">예측 정확도</h3>
                <p class="text-2xl">${Math.round(data.accuracy)}%</p>
            </div>
            <div class="bg-gray-700 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">RMSE</h3>
                <p class="text-2xl">${Math.round(data.metrics.rmse).toLocaleString()}원</p>
            </div>
        </div>

        <div class="bg-gray-700 p-4 rounded-lg mb-6">
            <h3 class="text-xl font-bold mb-4">최근 예측 결과</h3>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead>
                        <tr class="border-b border-gray-600">
                            <th class="p-2 text-left">날짜</th>
                            <th class="p-2 text-right">실제 가격</th>
                            <th class="p-2 text-right">예측 가격</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.recent_predictions.map(pred => `
                            <tr class="border-b border-gray-600">
                                <td class="p-2 text-left">${pred.date}</td>
                                <td class="p-2 text-right">${Math.round(pred.actual).toLocaleString()}원</td>
                                <td class="p-2 text-right">${Math.round(pred.predicted).toLocaleString()}원</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function showModal() {
    const modal = document.getElementById('predictionModal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}