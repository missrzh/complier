.386

.model flat, stdcall

option casemap:none

include C://masm32/include/windows.inc
include C://masm32/include/kernel32.inc
include C://masm32/include/user32.inc
include C://masm32/include/masm32.inc
include C://masm32/include/masm32rt.inc 

includelib C://masm32/lib/kernel32.lib
includelib C://masm32/lib/masm32.lib
includelib C://masm32/lib/user32.lib

main PROTO

.data

.code


start:
    invoke main
    fn MessageBox,0,str$(eax), "Lab5" ,MB_OK
    invoke ExitProcess, 0
    
gello PROC
push ebp
mov ebp, esp
mov eax, DWORD ptr[ebp+8]
.if eax == 0
mov eax, 5
.else
mov eax, 6
.endif
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp

ret
gello ENDP
main PROC
push ebp
mov ebp, esp
mov eax, 0
push eax
mov eax, 7
push eax
mov eax, DWORD ptr[ebp+-8]
push eax
mov eax, DWORD ptr[ebp+-4]

push eax
call gello
add esp, 4
mov ebx, eax
pop eax
sub eax, ebx
mov DWORD ptr[ebp+-8], eax
mov eax, DWORD ptr[ebp+-8]
mov esp, ebp
pop ebp
ret
mov esp, ebp
pop ebp

ret
main ENDP

END start