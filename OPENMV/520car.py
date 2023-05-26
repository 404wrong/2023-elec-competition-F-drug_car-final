from pyb import Pin, Timer,UART,LED
import sensor, image, time,pyb
from pid import PID

sensor.reset() # Initialize the camera sensor.
sensor.set_pixformat(sensor.RGB565) # use RGB565.
sensor.set_framesize(sensor.QQVGA) # use QQVGA for speed.
sensor.skip_frames(10) # Let new settings take affect.
sensor.set_auto_whitebal(False) # turn this off.
clock = time.clock() # Tracks FPS.

red_threshold= (8, 65, 48, 15, -38, 44)
size_threshold=1000
roi_cross=(0,0,80,5)
roi_line=(20,0,40,60)
rho_pid = PID(p=0.4, i=0)
theta_pid = PID(p=0.001, i=0)
uart=UART(3,19200)
LED(1).on()
LED(2).on()
LED(3).on()
sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()

ROI2=(0,0,60,50)
ROI1=(100,0,60,50)
ROI3=(60,0,40,200)
LEFT=-1
RIGHT=1
inverse_left=False
inverse_right=False
ain1 =  Pin('P0', Pin.OUT_PP)
ain2 =  Pin('P1', Pin.OUT_PP)
bin1 =  Pin('P2', Pin.OUT_PP)
bin2 =  Pin('P3', Pin.OUT_PP)
ain1.low()
ain2.low()
bin1.low()
bin2.low()
pwma = Pin('P7')
pwmb = Pin('P8')
tim = Timer(4, freq=1000)
ch1 = tim.channel(1, Timer.PWM, pin=pwma)
ch2 = tim.channel(2, Timer.PWM, pin=pwmb)
ch1.pulse_width_percent(0)
ch2.pulse_width_percent(0)
clock.tick()


uart = UART(3, 19200)


def run(left_speed, right_speed):
    if inverse_left==True:
        left_speed=(-left_speed)
    if inverse_right==True:
        right_speed=(-right_speed)
    if left_speed < 0:
        ain1.low()
        ain2.high()
    else:
        ain1.high()
        ain2.low()
    ch1.pulse_width_percent(int(abs(left_speed)))
    if right_speed < 0:
        bin1.low()
        bin2.high()
    else:
        bin1.high()
        bin2.low()
    ch2.pulse_width_percent(int(abs(right_speed)))



def turn(direction):
    #print(direction)
    if direction=='3':
        run(-50,50)
        a=15
    else:
        print('l')
        run(50,-50)
        a=-15
    time.sleep_ms(400)

    while 1:

        t=0
        start = pyb.millis()
        while pyb.elapsed_millis(start) < 800:
            img = sensor.snapshot().binary([red_threshold])
            line = img.get_regression([(40, 100)], roi=roi_line, robust=True)
            # run(0,0)
            time.sleep_ms(10)
            if line:
                if line.theta()>170 or line.theta()==0:
                    print("Azhongline")
                    print(line.theta())
                    time.sleep_ms(50)
                    run(0, 0)
                    t = 1
                    break
            run(a, -a)
            time.sleep_ms(10)
        if t == 1:
            break
        a = -a
    run(0,0)


def along(tt,type):
    print('along start')
    t=time.time_ns()
    print(t)
    #print(t)
    while (True):
        #print(time.time()-t)
        #print(time.time_ns()-t)
        if time.time_ns()-t>tt:
            print('tbreak')
            run(0,0)
            break
        data = uart.readline()
        if data is not None:
            if data.decode()[0] =='7':
                print('bbreak')
                run(0,0)
                break
        img = sensor.snapshot().binary([red_threshold])
        line = img.get_regression([(40, 100)], roi=roi_line, robust=True)
        if (line):
            #print("line")
            rho_err = abs(line.rho()) - img.width() / 2
            if line.theta() > 90:
                #print(line.theta())
                #print(2)
                theta_err = line.theta() - 180
                #print("line.theta()>90:")
            else:
                #print(1)
                theta_err = line.theta()
            img.draw_line(line.line(), color=127)
            # print(rho_err,line.magnitude(),rho_err)
            rho_output = rho_pid.get_pid(rho_err, 1)
            theta_output = theta_pid.get_pid(theta_err, 1)
            output = rho_output + theta_output
            run(50 + output, 50 - output)  # if want faster,change 50 to 70 or so
            #print("car.run(50+output, 50-output)")
        else:
            if type==1 :
                if time.time_ns()-t>10000000000:
                    print(1)
                    run(0,0)
                    break
                else:
                    run(0,0)
                    break
            else:
                run(50, 50)
            #break
            pass

def turn_back():
    run(50, -50)
    time.sleep_ms(650)
    a = 15
    while 1:
        t = 0
        start = pyb.millis()
        print("start")
        while pyb.elapsed_millis(start) < 1500:
            img = sensor.snapshot().binary([red_threshold])
            line = img.get_regression([(40, 100)], roi=roi_line, robust=True)
            # run(0,0)
            time.sleep_ms(10)
            if line:
                if line.theta()>170 or line.theta()==0:
                    print("Azhongline")
                    print(line.theta())
                    time.sleep_ms(50)
                    run(0, 0)
                    t = 1
                    break
            run(a, -a)
            time.sleep_ms(10)
        if t == 1:
            break
        a = -a

run(0, 0)
print('aline finished')

if __name__ == '__main__':
    dir=[]
    leng=[]
    while 1:
        data=uart.read(1)
        if data is not None:
            if data.decode()[0]=='1':
                along(10*1000000000,0)
            elif data.decode()[0]=='2':
                turn('2')
            elif data.decode()[0]=='3':
                turn('3')
            elif data.decode()[0]=='4':
                turn_back()
            elif data.decode()[0]=='5':
                along(15*100000000,0)
            elif data.decode()[0]=='6':
                along(8*100000000,0)
                run(50,50)
                time.sleep_ms(100)
                run(0,0)
            elif data.decode()[0]=='7':
                run(0,0)
            elif data.decode()[0]=='a':
                along(200*100000000,1)
                print('aaaa')
                run(50,50)
                time.sleep_ms(300)
                run(0,0)
            print(data.decode())
            print('111111111111111111111111111')



