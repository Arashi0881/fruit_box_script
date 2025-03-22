import cv2
import numpy as np
import pyautogui
from itertools import combinations
import time
import itertools

def find_numbers(screenshot, threshold=0.85):
    numbers = []
    detected_points = []

    for num in range(1, 10): 
        template_path = f"templates/{num}.png"  
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

        locations = np.where(result >= threshold)
        for pt in zip(*locations[::-1]): 
            center_x = pt[0] + template.shape[1] // 2
            center_y = pt[1] + template.shape[0] // 2

            is_duplicate = any(
                abs(center_x - x) <= 10 and abs(center_y - y) <= 10
                for _, (x, y) in detected_points
            )
            if not is_duplicate:
                detected_points.append((num, (center_x, center_y)))
                numbers.append((num, (center_x, center_y)))

    return numbers


def find_rectangle_combinations(numbers):
    combinations = []
   
    for (num1, coord1), (num2, coord2) in itertools.combinations(numbers, 2):
        # if abs(coord1[0] - coord2[0]) > 200 or abs(coord1[1] - coord2[1]) > 200:
        #     continue
        top_left_x = min(coord1[0]-39, coord2[0]-39)
        top_left_y = min(coord1[1]-39, coord2[1]-39)
        bottom_right_x = max(coord1[0]+38, coord2[0]+38)
        bottom_right_y = max(coord1[1]+38, coord2[1]+38)

        contained_numbers = [
            (num, coord) for num, coord in numbers
            if top_left_x <= coord[0] <= bottom_right_x and top_left_y <= coord[1] <= bottom_right_y
        ]

        total = sum(num for num, _ in contained_numbers)
        
        if total == 10:
            combinations.append(contained_numbers)

    return combinations



def draw_rectangle(combo):
    coordinates = [coord for _, coord in combo]

    min_x = min(coord[0] for coord in coordinates) 
    max_x = max(coord[0] for coord in coordinates) 
    min_y = min(coord[1] for coord in coordinates) 
    max_y = max(coord[1] for coord in coordinates) 

    start_x = min_x -15  
    start_y = min_y -15
    end_x = max_x + 60    
    end_y = max_y + 60

    pyautogui.moveTo(start_x, start_y, duration=0.0)


    pyautogui.mouseDown(start_x, start_y) 
    pyautogui.moveTo(end_x, end_y, duration=0.45)  
    time.sleep(0.05)  
    pyautogui.mouseUp() 
    pyautogui.moveTo(200, 200, duration=0.0)


def calculate_overlap(combo, combos):
    """
    Tính toán số lượng trùng lặp của một combo với các combo khác.
    """
    combo_coords = {coord for _, coord in combo}
    overlap_count = 0

    for other_combo in combos:
        other_coords = {coord for _, coord in other_combo}
        
        overlap_count += len(combo_coords & other_coords)

    return overlap_count


def main():

    print("Bắt đầu tự động chơi game. Nhấn Ctrl+C để thoát.")
    counter = 0
    try:
        while counter < 40:

            while counter < 40:
                screenshot = pyautogui.screenshot()
                screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
                numbers = find_numbers(screenshot)
                if not numbers:
                    print("Không tìm thấy số nào. Đang đợi...")
                    time.sleep(1)
                    break

                combos = find_rectangle_combinations(numbers)
                if not combos:
                    print("Không còn combo nào hợp lệ.")
                    break

                combo_overlap = [(combo, calculate_overlap(combo, combos)) for combo in combos]

                combo_overlap.sort(key=lambda x: x[1])

                draw_rectangle(combo_overlap[0][0])  
                if(len(combo_overlap) > 1 and counter > 20):
                    draw_rectangle(combo_overlap[1][0])
                    counter += 1 
                if(len(combo_overlap) > 2 and counter < 30):
                    draw_rectangle(combo_overlap[2][0]) 
                    counter += 1
                counter += 1
                time.sleep(0.1) 
        

        while True:  
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
            used_coords = set()  # Lưu tọa độ các số đã sử dụng
            completed_combos = []  
            numbers = find_numbers(screenshot)
            print(f"Tìm thấy {len(numbers)} số.")
            if not numbers:
                print("Không tìm thấy số nào........")
                time.sleep(1)
                continue


            combos = find_rectangle_combinations(numbers)
            print(f"Tìm thấy {len(combos)} combo.")

            for combo in combos:
                if all(coord not in used_coords for _, coord in combo):
                    draw_rectangle(combo) 
                    completed_combos.append(combo)  

                    for _, coord in combo:
                        used_coords.add(coord)
            combos = [
                combo for combo in combos
                if all(coord not in used_coords for _, coord in combo)
            ]

            time.sleep(0.1) 


    except KeyboardInterrupt:
        print("Dừng script.")



if __name__ == "__main__":
    main()
